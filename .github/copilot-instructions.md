# Mini-projekt — Aspekty prawne, społeczne i etyczne w AI

Repozytorium indywidualnego mini-projektu z kursu na Politechnice Wrocławskiej (2025/2026).

## Temat projektu

12. Prompt injection — testy bezpieczeństwa LLM. Wsparcie Copilota ma być ukierunkowane na defensywne testy bezpieczeństwa, analizę ryzyka i opis wniosków w kontekście prawa oraz etyki AI.

## Język

Odpowiadaj po polsku. Komentarze w kodzie, dokumentacja, docstringi — po polsku.

## Kontekst kursu

Kurs dotyczy prawa (RODO, AI Act, IP), etyki AI, licencji i odpowiedzialności za systemy AI. Mini-projekt powinien być powiązany z tą tematyką. Pomagając studentowi, zawsze odnoś się do aspektów prawnych/etycznych — to nie jest kurs programowania.

W projekcie 12 szczególny nacisk kładź na:

- odporność aplikacji LLM na prompt injection,
- ochronę danych osobowych i informacji poufnych,
- ograniczanie uprawnień modelu i separację instrukcji od danych,
- testy i dokumentowanie ryzyka przed wdrożeniem.

## Struktura

- `README.md` — opis projektu, wyniki, wnioski merytoryczne
- `PROCESS.md` — dokumentacja procesu pracy z AI (prompty, decyzje, iteracje)
- `AGENTS.md` — instrukcje dla agentów AI
- `LICENSE` — licencja akademicka (materiał dydaktyczny — omawia IP, RODO, AI Act)
- `pyproject.toml` — zależności Python (zarządzane przez `uv`)
- `.env.example` — wzór pliku ze zmiennymi środowiskowymi (klucze API)
- `src/` — kod źródłowy + przykłady wywołań API (OpenAI, Anthropic, Gemini)
- `notebooks/` — notebooki Jupyter
- `wyniki/` — artefakty (wykresy, tabelki, raporty)

## Ważne zasady

- PROCESS.md jest tak samo ważny jak kod — przypominaj studentowi o dokumentowaniu promptów i decyzji.
- Nie wklejaj outputu AI do PROCESS.md — tylko prompty studenta.
- Nie generuj fałszywych wyników — uruchamiaj kod.
- Oddanie projektu: `/submit-solution`
