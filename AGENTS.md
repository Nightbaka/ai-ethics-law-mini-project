# AGENTS.md

Instrukcje dla agentów AI (Claude Code, Cursor, Copilot, Aider itp.) pracujących w tym repozytorium.

## Kontekst projektu

To jest repozytorium **indywidualnego mini-projektu** z kursu "Aspekty prawne, społeczne i etyczne w sztucznej inteligencji" (Politechnika Wrocławska, semestr letni 2025/2026). Prowadzący: Łukasz Augustyniak.

**Repozytorium szablonu:** [github.com/laugustyniak/ai-ethics-law-mini-project](https://github.com/laugustyniak/ai-ethics-law-mini-project)

Mini-projekt jest powiązany z tematyką kursu: prawo (RODO, AI Act, IP), etyka AI, licencje, odpowiedzialność za systemy AI.

## Język

Cała dokumentacja, komentarze w kodzie i komunikacja — **po polsku**.
Kod - english (np. nazwy funkcji, zmiennych) — dowolny, ale komentarze i markdown po polsku.

## Szybkie komendy

```bash
uv sync
uv sync --extra notebooks
uv run src/example_openai.py
```

## Kluczowe pliki

- [README.md](README.md) — wymagane sekcje, uruchomienie, wnioski
- [PROCESS.md](PROCESS.md) — prompty, decyzje, błędy, iteracje (bez outputu AI)
- [.claude/CLAUDE.md](.claude/CLAUDE.md) — zasady kursu i praca z AI

## Struktura repozytorium

```
.
├── AGENTS.md          # Ten plik — instrukcje dla agentów AI
├── README.md          # Opis projektu, jak uruchomić, wnioski
├── PROCESS.md         # Dokumentacja procesu pracy z AI
├── LICENSE            # Licencja akademicka (przeczytaj — to materiał dydaktyczny!)
├── pyproject.toml     # Zależności Python (zarządzane przez uv)
├── .env.example       # Wzór pliku ze zmiennymi środowiskowymi (klucze API)
├── src/               # Kod źródłowy + przykłady wywołań API (OpenAI, Anthropic, Gemini)
├── notebooks/         # Notebooki Jupyter (.ipynb)
└── wyniki/            # Wykresy, tabelki, raporty, screenshoty
```

## Co powinno być w każdym pliku

### README.md

Główny dokument projektu. Musi zawierać:

1. **Tytuł i autor** — nazwa mini-projektu, imię i nazwisko, numer indeksu
2. **Temat** — który temat z menu wybrano (1-29) lub opis własnego tematu
3. **Cel projektu** — co mini-projekt robi i po co, 2-3 zdania
4. **Wymagania i uruchomienie** — jak zainstalować zależności i uruchomić kod/notebook:
   - `uv sync` (zależności w `pyproject.toml`)
   - Komendy do uruchomienia
   - Wymagane zmienne środowiskowe / klucze API (bez wartości!)
5. **Wyniki** — najważniejsze wyniki, wnioski, wizualizacje (lub linki do plików w `wyniki/`)
6. **Wnioski merytoryczne** — co wynika z analizy w kontekście prawa/etyki/regulacji AI:
   - Powiązanie z projektem grupowym (jeśli dotyczy)
   - Konkretne rekomendacje lub obserwacje
7. **Ograniczenia** — czego projekt nie robi, co można by rozszerzyć
8. **Źródła** — linki do wykorzystanych materiałów, dokumentów prawnych, datasetów

**Ocena:** Pokrywa kryteria z "Merytoryka i głębokość analizy" (40 pkt) oraz częściowo "Techniczna realizacja" (20 pkt).

### PROCESS.md

Dokumentacja procesu pracy — **tak samo ważna jak kod**. Musi zawierać:

1. **Narzędzia AI** — lista narzędzi AI użytych w projekcie (np. Claude Code, Cursor, ChatGPT, Copilot) i do czego każde służyło
2. **Prompty** — rzeczywiste prompty użyte podczas pracy:
   - Nie wklejaj outputu z AI — tylko prompty, które wpisywałeś
   - Pogrupuj prompty tematycznie (np. "generowanie kodu", "analiza wyników", "debugowanie")
3. **Decyzje** — kluczowe decyzje podjęte w trakcie pracy:
   - Dlaczego wybrano dane podejście/bibliotekę/metodę?
   - Jakie alternatywy rozważano?
4. **Co nie zadziałało** — ślepe uliczki, błędy, nieudane podejścia:
   - Co poszło nie tak?
   - Jak to naprawiono / obejdziono?
5. **Iteracje** — jak projekt ewoluował od pierwszej wersji do finalnej
6. **Czas pracy** — orientacyjny czas poświęcony na projekt (opcjonalne)

**Ocena:** Pokrywa kryteria z "Proces i dokumentacja" (40 pkt). Prowadzący chce zobaczyć świadome korzystanie z narzędzi AI.

### src/

Kod źródłowy projektu:

- Skrypty Python (.py), JavaScript (.js), TypeScript (.ts), Bash (.sh) lub inne
- Zależności Python definiowane w `pyproject.toml` (projekt korzysta z `uv`)
- Pliki `example_openai.py`, `example_anthropic.py`, `example_gemini.py` — startowe przykłady wywołań API LLM
- Klucze API w pliku `.env` (nie commitować! — wzór w `.env.example`)
- Kod powinien być czytelny i skomentowany po polsku
- Nie musi być produkcyjny — ważniejsza jest czytelność niż optymalizacja

### notebooks/

Notebooki Jupyter (.ipynb):

- Alternatywa lub uzupełnienie dla kodu w `src/`
- Notebook z komentarzami w markdown cells wystarczy jako forma oddania
- Wyniki (wykresy, tabelki) powinny być widoczne w renderowanym notebooku
- Jeśli notebook jest główną formą pracy, nie trzeba duplikować kodu w `src/`

### wyniki/

Artefakty wygenerowane przez projekt:

- Wykresy i wizualizacje (.png, .svg, .html)
- Tabelki wyników (.csv, .json)
- Raporty (.md, .pdf)
- Screenshoty z działania narzędzia
- Dane wyjściowe (nie wrzucaj dużych plików >10 MB — użyj .gitignore)

## Kryteria oceny (kontekst dla agenta)

Agent powinien pomagać studentowi pokryć wszystkie kryteria:

| Kryterium | Punkty | Gdzie w repo |
|-----------|--------|-------------|
| Proces i dokumentacja | 40 pkt | PROCESS.md |
| Merytoryka i głębokość analizy | 40 pkt | README.md (wnioski), notebooks/ |
| Techniczna realizacja | 20 pkt | src/, notebooks/ |

### Skalowanie ocen

- **Base (50-60%)** — podstawowa implementacja, działa, udokumentowana, ma wnioski
- **Good (70-80%)** — głębsza analiza, porównanie podejść, więcej danych, lepsze wnioski
- **Excellent (90-100%)** — kompleksowe podejście, twórcze rozwiązanie, pogłębiona analiza

## Zasady dla agenta

1. **Nie generuj fałszywych wyników** — jeśli analiza wymaga uruchomienia kodu, uruchom go. Nie zmyślaj danych ani metryk.
2. **Dokumentuj swoje użycie** — student musi wpisać w PROCESS.md jakie prompty Ci dawał. Przypominaj o tym.
3. **Pisz po polsku** — komentarze w kodzie, docstringi, markdown — wszystko po polsku.
4. **Nie usuwaj AGENTS.md** — ten plik jest częścią szablonu.
5. **Powiązanie z kursem** — zawsze pytaj studenta o powiązanie z projektem grupowym i aspektami prawnymi/etycznymi. To jest kurs o aspektach AI, nie o programowaniu.
6. **Stawiaj na wnioski** — kod jest środkiem do celu. Celem jest analiza i wnioski merytoryczne.
