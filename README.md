# Mini-projekt 12 — Testy bezpieczeństwa LLM wobec prompt injection

**Autor:** [Marek Fiuk], nr indeksu: [266595]

**Temat:** 12 — Prompt injection — testy bezpieczeństwa LLM

**Kurs:** Aspekty prawne, społeczne i etyczne w AI, PWr 2025/2026

> Lista tematów: [Zasady zaliczenia — Menu mini-projektów](https://github.com/laugustyniak/ai-ethics-law-course/blob/main/Zasady%20zaliczenia.md#menu-mini-projekt%C3%B3w)

---

## Quick Start

```bash
uv sync                        # zainstaluj zależności
cp .env.example .env           # skopiuj wzór zmiennych środowiskowych
# uzupełnij klucze API w .env

uv run src/example_openai.py   # sprawdź że działa (OpenAI)
uv run src/example_anthropic.py  # lub Anthropic
uv run src/example_gemini.py     # lub Gemini
```

---

## Cel projektu

Projekt analizuje odporność LLM na ataki typu prompt injection. Celem jest przygotowanie zestawu testów bezpieczeństwa, które pokazują, jak zmienia się zachowanie modelu po dodaniu zabezpieczeń, takich jak izolacja instrukcji systemowych, filtrowanie wejścia i walidacja odpowiedzi.

## Powiązanie z projektem grupowym

Wybrałem ten temat, ze względu na ogólne zainteresowanie działaniem llm-ów i kwestiami bezpieczeństwa związanymi z ich użyciem. Obecnie trudno jest programować nie używając llm-ów ze względu na to jak bardzo ułatwiają one pracę, ale czy nie wystawiamy się na ryzyko ataku ze złośliwej strony/skilla? Temat niepowiązany z projektem grupowym. 

## Wymagania

Projekt korzysta z [uv](https://docs.astral.sh/uv/) — szybkiego menedżera pakietów Python.

```bash
# Instalacja uv (jeśli nie masz)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Instalacja zależności
uv sync

# Z notebookami Jupyter
uv sync --extra notebooks
```

**Zmienne środowiskowe** — skopiuj plik `.env.example` i uzupełnij klucze API:

```bash
cp .env.example .env
# Uzupełnij klucze w .env (OpenAI / Anthropic / Google — w zależności od projektu)
```

## Uruchomienie

```bash
# Główny skrypt (zamień na swój po implementacji)
uv run src/main.py

# lub notebook
uv run jupyter notebook notebooks/analiza.ipynb

# benchmark prompt injection
uv run src/run_prompt_injection.py --limit 100 --model-kind echo --local-cache data/train.parquet

# pierwszy lokalny model na GPU 8 GB
uv run src/run_prompt_injection.py --limit 20 --model-kind transformers --model-preset first-local --local-cache data/train.parquet

# alternatywa: Qwen 1.5B, nadal lekki lokalny model
uv run src/run_prompt_injection.py --limit 20 --model-kind transformers --model-preset qwen2-5-1-5b --local-cache data/train.parquet

# mocniejszy model lokalny po weryfikacji pamięci
uv run src/run_prompt_injection.py --limit 20 --model-kind transformers --model-preset mistral-7b --load-in-4bit --local-cache data/train.parquet
```

## Wyniki

[Najważniejsze wyniki — tabelki, wykresy, liczby. Wstaw bezpośrednio lub linkuj do plików w `wyniki/`.]

## Wnioski merytoryczne

[Kluczowa sekcja — co wynika z analizy w kontekście prawa / etyki / regulacji AI? Konkretne obserwacje i rekomendacje.]

## Ograniczenia

[Czego projekt nie robi? Co można by rozszerzyć? Bądź uczciwy.]

## Źródła

- [Nazwa źródła](URL) — krótki opis
