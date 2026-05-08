"""
CLI do uruchamiania benchmarku prompt injection.

Testuje model przez adapter i ocenia odpowiedzi za pomocą sędziego LLM.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from judge import create_judge
from prompt_injection_harness import load_examples, load_dataset_records, run_benchmark, save_records
from prompt_injection_models import EchoModelAdapter, TransformersLocalAdapter, get_local_model_preset


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Benchmark prompt injection dla modeli LLM")
    parser.add_argument("--dataset", default="guychuk/open-prompt-injection", help="Nazwa datasetu z Hugging Face")
    parser.add_argument("--split", default="train", help="Split datasetu")
    parser.add_argument("--limit", type=int, default=100, help="Liczba przykładów do przetworzenia")
    parser.add_argument("--output-dir", default="wyniki/prompt_injection", help="Katalog wyników")
    parser.add_argument("--local-cache", default="data/train.parquet", help="Lokalny cache parquet dla datasetu")
    parser.add_argument("--model-kind", choices=("echo", "transformers"), default="transformers", help="Typ adaptera modelu")
    parser.add_argument("--model-preset", default="first-local", help="Preset modelu lokalnego, np. first-local, tinyllama, mistral-7b")
    parser.add_argument("--model-name", default=None, help="Nazwa modelu lokalnego dla transformers (nadpisuje preset)")
    parser.add_argument("--load-in-8bit", action="store_true", help="Ładuj model w 8-bit, jeśli wspierane")
    parser.add_argument("--load-in-4bit", action="store_true", help="Ładuj model w 4-bit, jeśli wspierane")
    parser.add_argument("--judge-model", default="TinyLlama/TinyLlama-1.1B-Chat-v1.0", help="Model do użycia jako sędzia")
    parser.add_argument("--judge-load-in-4bit", action="store_true", help="Ładuj model sędziego w 4-bit")
    parser.add_argument("--judge-echo", action="store_true", help="Testowy sędzia (bez ładowania modelu)")
    parser.add_argument("--no-sanitize", action="store_true", help="Wyłącz sanitizację promptów wejściowych")
    return parser


def create_adapter(args: argparse.Namespace):
    if args.model_kind == "echo":
        return EchoModelAdapter()
    preset = get_local_model_preset(args.model_preset)
    model_name = args.model_name or preset.model_name
    return TransformersLocalAdapter(
        model_name=model_name,
        load_in_8bit=args.load_in_8bit or preset.recommended_precision == "8bit",
        load_in_4bit=args.load_in_4bit or preset.recommended_precision == "4bit",
        name=f"{preset.name}:{model_name}",
    )


def main() -> int:
    args = build_parser().parse_args()
    dataset = load_dataset_records(args.dataset, split=args.split, local_cache_path=args.local_cache)
    examples = load_examples(dataset, limit=args.limit)
    adapter = create_adapter(args)
    judge = create_judge(model_name=args.judge_model, load_in_4bit=args.judge_load_in_4bit, echo=args.judge_echo)

    records = run_benchmark(
        adapter=adapter,
        examples=examples,
        judge=judge,
        sanitize_inputs=not args.no_sanitize,
    )
    save_records(records, Path(args.output_dir))

    print(f"Przetworzono {len(records)} przykładów. Wyniki zapisano do {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())