"""
Harness do testów prompt injection na datasetach Hugging Face.

Moduł ładuje próbki, uruchamia model przez adapter i zapisuje wyniki do CSV/JSONL.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Literal, Sequence

import pandas as pd

from judge import JudgeClassification, LLMJudge
from prompt_injection_filters import sanitize_text
from prompt_injection_models import ModelAdapter, create_default_system_prompt


PROMPT_FIELD_CANDIDATES = ("prompt", "text", "input", "query", "instruction", "content", "message", "data")
LABEL_FIELD_CANDIDATES = ("label", "target", "answer", "class", "is_prompt_injection", "prompt_injection", "malicious")
TEXT_COLLECTION_FIELDS = ("conversation", "messages", "context", "metadata")


@dataclass(frozen=True)
class AttackExample:
    """Ujednolicony przykład z datasetu."""

    example_id: str
    prompt: str
    label: str | None = None
    source: str | None = None
    attack_type: str | None = None
    is_attack: bool | None = None
    reference_prompt: str | None = None
    instruction: str | None = None


@dataclass(frozen=True)
class RunRecord:
    """Jeden wynik wykonania modelu na przykładzie."""

    example_id: str
    prompt: str
    label: str | None
    attack_type: str | None
    ground_truth_attack: bool
    model_name: str
    system_prompt: str
    sanitized_prompt: str
    response: str
    judge_classification: Literal["reject", "harmful", "accept"]
    judge_reasoning: str | None
    response_length: int
    # Pola związane z heurystycznymi zabezpieczeniami (opcjonalne)
    heuristic_injection_hits: tuple[str, ...] | None = None
    heuristic_command_hits: tuple[str, ...] | None = None
    heuristic_pii_hits: tuple[str, ...] | None = None
    # Co by zostało zastosowane jako skuteczna decyzja zabezpieczeń (może różnić się od judge_classification)
    effective_classification: Literal["reject", "harmful", "accept"] | None = None
    effective_reasoning: str | None = None


@dataclass(frozen=True)
class CachedPromptResult:
    """Wynik modelu cache'owany dla powtarzających się promptów."""

    response: str


def _pick_first_string_value(example: dict, candidates: Sequence[str]) -> str | None:
    for key in candidates:
        value = example.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return None


def _stringify_iterable(value: Iterable[object]) -> str:
    return "\n".join(str(item) for item in value if item is not None)


def normalize_example(example: dict, index: int) -> AttackExample:
    """Konwertuje dowolny rekord na kanoniczny przykład testowy."""

    has_attack_columns = "attack_input" in example and "normal_input" in example
    if has_attack_columns:
        instruction = example.get("instruction")
        attack_prompt = example.get("attack_input")
        normal_prompt = example.get("normal_input")
        if isinstance(attack_prompt, str) and attack_prompt.strip():
            attack_type = _pick_first_string_value(example, ("attack_type", "injected_task", "task_type"))
            reference_prompt = normal_prompt if isinstance(normal_prompt, str) and normal_prompt.strip() else None
            is_attack = reference_prompt is None or attack_prompt != reference_prompt or bool(attack_type)
            return AttackExample(
                example_id=str(example.get("sample_id", example.get("id", index))),
                prompt=attack_prompt,
                label=_pick_first_string_value(example, ("label", "task_type", "injected_task")),
                source="attack_input",
                attack_type=attack_type,
                is_attack=is_attack,
                reference_prompt=reference_prompt,
                instruction=instruction,
            )
    
    raise ValueError(f"Nie można znaleźć odpowiednich pól promptu w przykładzie: {example}")


def load_examples(dataset, limit: int | None = None, stratify_attacks: bool = True) -> list[AttackExample]:
    """Normalizuje dane z datasetu Hugging Face."""



    rows = []

    if stratify_attacks:
        attack_types = set()
        injected_tasks = set()
        for example in dataset:
            attack_types.add(example.get("attack_type"))
            injected_tasks.add(example.get("injected_task"))
        
        # stratyfikacja po każdym attack_type i injected_task
        combinations = [(at, it) for at in attack_types for it in injected_tasks]
        for attack_type, injected_task in combinations:
            filtered = [example for example in dataset if example['attack_type'] == attack_type and example['injected_task'] == injected_task]
            for i in range(min(limit or 0, len(filtered))):
                rows.append(normalize_example(filtered[i], i))

    else:
        for index, example in enumerate(dataset):
            rows.append(normalize_example(example, index))
            if limit is not None and len(rows) >= limit:
                break

    return rows


def run_benchmark(
    adapter: ModelAdapter,
    examples: Sequence[AttackExample],
    judge: LLMJudge,
    system_prompt: str | None = None,
    sanitize_inputs: bool = True,
    enable_heuristics: bool = False,
    heuristic_reject: bool = False,
) -> list[RunRecord]:
    """Uruchamia model na przykładach i ocenia odpowiedzi za pomocą sędziego."""

    active_system_prompt = system_prompt or create_default_system_prompt()
    records: list[RunRecord] = []
    prompt_cache: dict[tuple[str, str, str], CachedPromptResult] = {}

    # Phase 1: generate all model responses (load model once if adapter supports it)
    generated_results: list[dict] = []

    # Try to pre-load adapter model if it exposes a _load() method (saves repeated loads)
    try:
        if hasattr(adapter, "_load"):
            getattr(adapter, "_load")()
    except Exception:
        # Nie przerywamy jeśli pre-load nie powiódł się; fallback do generate()
        pass

    for example in examples:
        instruction_prefix = f"[{example.instruction}]\n" if example.instruction else ""
        active_system_prompt_with_instruction = instruction_prefix + example.prompt
        sanitized_prompt = sanitize_text(active_system_prompt_with_instruction) if sanitize_inputs else active_system_prompt_with_instruction
        cache_key = (adapter.name, active_system_prompt_with_instruction, sanitized_prompt)
        cached_result = prompt_cache.get(cache_key)
        if cached_result is None:
            response = adapter.generate(active_system_prompt, sanitized_prompt)
            cached_result = CachedPromptResult(response=response)
            prompt_cache[cache_key] = cached_result
        else:
            response = cached_result.response

        generated_results.append(
            {
                "example": example,
                "response": response,
                "sanitized_prompt": sanitized_prompt,
                "system_prompt_with_instruction": active_system_prompt_with_instruction,
            }
        )

    # If adapter exposes close(), call it to release weights before loading judge
    try:
        if hasattr(adapter, "close"):
            getattr(adapter, "close")()
    except Exception:
        pass

    # Phase 2: load judge (it will cache its model internally) and classify all outputs
    try:
        if hasattr(judge, "_ensure_model_loaded"):
            getattr(judge, "_ensure_model_loaded")()
    except Exception:
        pass

    for entry in generated_results:
        example: AttackExample = entry["example"]
        response: str = entry["response"]
        sanitized_prompt: str = entry["sanitized_prompt"]

        # Ustal ground truth z metadanych datasetu
        ground_truth_attack = example.is_attack if example.is_attack is not None else False

        # Wyznacz ground truth label dla sędziego
        ground_truth_label: str | None = None
        if example.source == "attack_input":
            ground_truth_label = "harmful"
        elif example.source == "normal_input":
            ground_truth_label = "normal"
        elif example.is_attack:
            ground_truth_label = "harmful"

        # Poproś sędziego o ocenę (judge jest używany WYŁĄCZNIE do metryk)
        judge_result = judge.classify(
            ground_truth_label=ground_truth_label,
            system_prompt=active_system_prompt,
            user_prompt=sanitized_prompt,
            model_response=response,
        )

        # Domyślne wartości dotyczące heurystyk
        heuristic_injection_hits = None
        heuristic_command_hits = None
        heuristic_pii_hits = None
        effective_class = judge_result.value
        effective_reason = judge_result.reasoning

        if enable_heuristics:
            # import tutaj, ponieważ moduł może być opcjonalny
            from prompt_injection_filters import detect_prompt_injection

            detection = detect_prompt_injection(response)
            heuristic_injection_hits = detection.injection_hits
            heuristic_command_hits = detection.command_hits
            heuristic_pii_hits = detection.pii_hits

            # Jeśli włączono wymuszone odrzucenie, symulujemy zastosowanie tej obrony
            if heuristic_reject and (detection.has_injection_signal or detection.has_command_signal or detection.has_pii_signal):
                effective_class = "reject"
                effective_reason = (
                    f"heuristic_reject: injection_hits={heuristic_injection_hits}, "
                    f"command_hits={heuristic_command_hits}, pii_hits={heuristic_pii_hits}"
                )

        records.append(
            RunRecord(
                example_id=example.example_id,
                prompt=example.prompt,
                label=example.label,
                attack_type=example.attack_type,
                ground_truth_attack=ground_truth_attack,
                model_name=adapter.name,
                system_prompt=active_system_prompt,
                sanitized_prompt=sanitized_prompt,
                response=response,
                judge_classification=judge_result.value,
                judge_reasoning=judge_result.reasoning,
                response_length=len(response),
                heuristic_injection_hits=heuristic_injection_hits,
                heuristic_command_hits=heuristic_command_hits,
                heuristic_pii_hits=heuristic_pii_hits,
                effective_classification=effective_class,
                effective_reasoning=effective_reason,
            )
        )

    return records


def summarize_records(records: Sequence[RunRecord]) -> dict[str, object]:
    """Tworzy zestaw metryk z wyników benchmarku oparte na ocenie sędziego."""

    total = len(records)
    if total == 0:
        return {
            "total_examples": 0,
            "mean_response_length": 0.0,
            "rejection_rate": 0.0,
            "harmful_response_rate": 0.0,
            "safe_response_rate": 0.0,
        }

    rejection_count = sum(1 for record in records if record.judge_classification == "reject")
    harmful_count = sum(1 for record in records if record.judge_classification == "harmful")
    safe_count = sum(1 for record in records if record.judge_classification == "accept")

    return {
        "total_examples": total,
        "mean_response_length": sum(record.response_length for record in records) / total,
        "rejection_rate": rejection_count / total,
        "harmful_response_rate": harmful_count / total,
        "safe_response_rate": safe_count / total,
    }


def save_records(records: Sequence[RunRecord], output_dir: Path, write_summary: bool = False) -> None:
    """Zapisuje wyniki do CSV, JSONL i Parquet."""

    output_dir.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame([asdict(record) for record in records])

    csv_path = output_dir / "benchmark_results.csv"
    jsonl_path = output_dir / "benchmark_results.jsonl"
    parquet_path = output_dir / "benchmark_results.parquet"
    summary_path = output_dir / "benchmark_summary.json"

    frame.to_csv(csv_path, index=False)
    frame.to_json(jsonl_path, orient="records", lines=True, force_ascii=False)
    frame.to_parquet(parquet_path, index=False)
    if write_summary:
        summary_path.write_text(json.dumps(summarize_records(records), ensure_ascii=False, indent=2), encoding="utf-8")


def load_dataset_records(
    dataset_name: str,
    split: str = "train",
    local_cache_path: str | Path | None = None,
):
    """Ładuje dataset najpierw z lokalnego cache, a dopiero potem z Hugging Face.

    Jeśli istnieje lokalny plik parquet, unikamy kosztownego sprawdzania sieci i
    korzystamy z wersji już pobranej do repozytorium. Gdy pliku nie ma, fallback
    idzie do `datasets.load_dataset`.
    """

    cache_path = Path(local_cache_path) if local_cache_path is not None else Path("data") / f"{split}.parquet"
    if cache_path.exists():
        frame = pd.read_parquet(cache_path)
        return frame.to_dict(orient="records")

    try:
        from datasets import load_dataset
    except Exception as exc:  # pragma: no cover - zależne od środowiska
        raise RuntimeError("Brak pakietu `datasets`. Uruchom `uv sync`, aby go doinstalować.") from exc

    return load_dataset(dataset_name, split=split)


def load_hf_dataset(dataset_name: str, split: str = "train"):
    """Zachowana nazwa wstecznie zgodna z wcześniejszym API modułu."""

    return load_dataset_records(dataset_name=dataset_name, split=split)
