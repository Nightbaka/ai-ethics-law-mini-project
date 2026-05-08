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
            )

    prompt = _pick_first_string_value(example, PROMPT_FIELD_CANDIDATES)
    if prompt is None:
        for key in TEXT_COLLECTION_FIELDS:
            value = example.get(key)
            if isinstance(value, list) and value:
                prompt = _stringify_iterable(value)
                break
    if prompt is None:
        string_parts = [str(value) for value in example.values() if isinstance(value, str) and value.strip()]
        prompt = "\n".join(string_parts).strip()
    if not prompt:
        raise ValueError("Nie udało się wyłuskać treści promptu z rekordu datasetu")

    label = _pick_first_string_value(example, LABEL_FIELD_CANDIDATES)
    if label is None:
        for key in LABEL_FIELD_CANDIDATES:
            value = example.get(key)
            if isinstance(value, (int, float, bool)):
                label = str(value)
                break

    source = _pick_first_string_value(example, ("source", "dataset", "origin", "domain"))
    attack_type = _pick_first_string_value(example, ("attack_type", "injected_task", "task_type"))
    return AttackExample(
        example_id=str(example.get("id", index)),
        prompt=prompt,
        label=label,
        source=source,
        attack_type=attack_type,
        is_attack=None,
        reference_prompt=None,
    )


def load_examples(dataset, limit: int | None = None) -> list[AttackExample]:
    """Normalizuje dane z datasetu Hugging Face."""

    rows = []
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
) -> list[RunRecord]:
    """Uruchamia model na przykładach i ocenia odpowiedzi za pomocą sędziego."""

    active_system_prompt = system_prompt or create_default_system_prompt()
    records: list[RunRecord] = []
    prompt_cache: dict[tuple[str, str, str], CachedPromptResult] = {}

    for example in examples:
        sanitized_prompt = sanitize_text(example.prompt) if sanitize_inputs else example.prompt
        cache_key = (adapter.name, active_system_prompt, sanitized_prompt)
        cached_result = prompt_cache.get(cache_key)
        if cached_result is None:
            response = adapter.generate(active_system_prompt, sanitized_prompt)
            cached_result = CachedPromptResult(response=response)
            prompt_cache[cache_key] = cached_result
        else:
            response = cached_result.response

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

        # Poproś sędziego o ocenę
        judge_result = judge.classify(
            ground_truth_label=ground_truth_label,
            system_prompt=active_system_prompt,
            user_prompt=sanitized_prompt,
            model_response=response,
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


def save_records(records: Sequence[RunRecord], output_dir: Path) -> None:
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
