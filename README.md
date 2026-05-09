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
# benchmark prompt injection
uv run src/run_prompt_injection.py --limit 100 --model-kind echo --local-cache data/train.parquet

# pierwszy lokalny model na GPU 8 GB
uv run src/run_prompt_injection.py --limit 20 --model-kind transformers --model-preset first-local --local-cache data/train.parquet

# alternatywa: Qwen 1.5B, nadal lekki lokalny model
uv run src/run_prompt_injection.py --limit 20 --model-kind transformers --model-preset qwen2-5-1-5b --local-cache data/train.parquet

# mocniejszy model lokalny po weryfikacji pamięci
uv run src/run_prompt_injection.py --limit 20 --model-kind transformers --model-preset mistral-7b --load-in-4bit --local-cache data/train.parquet

# testy na wszystkich modelach i konfiguracjach (może zająć dużo czasu)
uv run src/run_exp.py
```

## Wyniki

[Najważniejsze wyniki — tabelki, wykresy, liczby. Wstaw bezpośrednio lub linkuj do plików w `wyniki/`.]

### Użycie modelu sędziego do wykrywania przekroczenia zabezpieczeń
Skuteczne zaimplementowanie sędziego wymagało dostrajania prompta do konkretnego modelu - na początku tinyllm odmawiał klasyfikacji. Następnie kiedy próbowałem zmienić sędziego na lepszy(w moim mniemaniu) model qwen3-1-7b, okazało się że jest niemożliwe, gdyż każdą odpowiedź klasyfikował jako szkodliwą. Ze względu na ograniczenia czasowe i zasobowe, ostatecznie zdecydowałem się na TinyLlama jako sędziego, ale nie jest to rozwiązanie idealne patrząc na przykładowe wyjście ![klasyfikacji](wyniki/final/sedzia.png).

### Usunięcie defensywnego prompta ostrzegającego model, przed atakiem nie przyniosło jednoznacznie lepszych wyników.

Dodanie prostego prompta systemowego, który instruuje model, aby nie wykonywał poleceń z promptów użytkownika, miało różne działanie w zalezności od modelu. W przypadku gemmy wywołało odwrotny efekt od spodziewanego - zmniejszyło liczbę odmów na szkodliwe prompty. Natomiast w przypadku tinyllamy, Zarówno liczba odmów i szkodliwych wyjść zwiększyła się.
![defensive prompt](wyniki/final/system.png)

### Różne modele są podatne na różne ataki, a qwen jest najbardziej podatny

![Procent szkodliwych odpowiedzi z podziałem na modele i sposób ataku](wyniki/final/qwen_vulnerable.png)

Qwen udzielił najwięcej szkodliwych odpowiedzi a co więcej ani razu jej nie odmówił. Może to wynikać z braku treningu do odmawiania na szkodliwe zapytanie.

![Qwen nie odmawia](wyniki/final/qwen_refusal.png)

## Wnioski merytoryczne

[Kluczowa sekcja — co wynika z analizy w kontekście prawa / etyki / regulacji AI? Konkretne obserwacje i rekomendacje.]
Qwen 1.7B nie nadaje się do użycia w środowisku w którym istnieje ryzyko ataku prompt injection, nawet z prostymi zabezpieczeniami, otwieramy się w ten samy na cyberatak. Ogólnie modele są mało odporne i żadnego nie udało mi się w pęłni zabezpieczyć, co podkreśla wagę monitorowania działań modeli i ograniczania ich systemów do dostępu do niesprawdzonych źródeł. Przed używaniem jakiegokolwiek modelu należałoby zbadać jak reaguje na takie problemy wstrzyknięcia złośliwej instrukcji, gdyż nawet w wewnętrznych źródłach danych mogą się znaleźć zanieczyszczone dane, które mogą spowodować niepożądane zachowanie modelu.

## Ograniczenia

Model sędziego jest najsłabszym modelem ze wszystkich, co wpływa na wiarygodność klasyfikacji. Brakuje dodatkowych sposobów zabezpieczenia modeli i dostosowania do ich API. Wykorzystany niewielki podzbiór, ze względu na ograniczenie zasobów. Brak testów na bezpiecznych promptów dla porównania.

## Źródła

- [guychuk/open-prompt-injection (Hugging Face Datasets)](https://huggingface.co/datasets/guychuk/open-prompt-injection) — główny dataset użyty do testów prompt injection (split train, lokalnie cache'owany do `data/train.parquet`).
