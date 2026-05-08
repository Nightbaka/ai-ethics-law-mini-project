---
name: submit-solution
description: >
  Walidacja i oddanie mini-projektu. Użyj gdy student chce oddać / złożyć / submitować rozwiązanie
  mini-projektu, lub gdy pisze /submit-solution. Skill sprawdza kompletność plików (README.md,
  PROCESS.md, wyniki/), obecność numeru indeksu, i dodaje prowadzącego (laugustyniak) jako
  collaboratora do repozytorium GitHub.
---

# Submit Solution — oddanie mini-projektu

Skill walidujący kompletność mini-projektu i dodający prowadzącego do repozytorium.

## Procedura

Wykonaj kroki **sekwencyjnie**. Zatrzymaj się na pierwszym błędzie krytycznym i poproś studenta o poprawki.

### Krok 1: Sprawdź repozytorium GitHub

1. Uruchom `gh repo view --json name,owner,url,isPrivate` aby potwierdzić, że jesteś w repozytorium GitHub.
2. Jeśli komenda się nie powiedzie — poinformuj studenta, że musi być w sklonowanym repozytorium GitHub.

### Krok 2: Walidacja plików

Uruchom skrypt walidacji:

```bash
python3 .github/skills/submit-solution/scripts/validate.py
```

Skrypt sprawdza:
- **README.md** — czy placeholdery `[Tytuł mini-projektu]`, `[Imię Nazwisko]`, `[XXXXXX]` zostały zastąpione
- **README.md** — czy numer indeksu (6 cyfr) jest obecny
- **PROCESS.md** — czy sekcje "Narzędzia AI", "Prompty", "Decyzje" zawierają treść (nie tylko nagłówki)
- **wyniki/** — czy katalog zawiera co najmniej 1 plik (poza .gitkeep)
- **src/ lub notebooks/** — czy student dodał własny kod (pliki example_*.py z szablonu nie są liczone)

Jeśli skrypt zgłosi błędy — wypisz je studentowi w czytelnej formie i **zatrzymaj się**. Nie kontynuuj do kroku 3.

### Krok 3: Sprawdź nieskomitowane zmiany

1. Uruchom `git status`
2. Jeśli są nieskomitowane zmiany — zapytaj studenta czy chce je skomitować przed oddaniem.

### Krok 4: Dodaj prowadzącego jako collaboratora

1. Uruchom:
   ```bash
   gh api repos/{owner}/{repo}/collaborators/laugustyniak -X PUT -f permission=push
   ```
2. Jeśli prowadzący jest już dodany — poinformuj o tym.
3. Jeśli komenda się nie powiedzie (np. brak uprawnień) — wyjaśnij studentowi jak dodać collaboratora ręcznie:
   - Settings → Collaborators → Add people → `laugustyniak`

### Krok 5: Podsumowanie

Wyświetl podsumowanie w formacie:

```
Oddanie mini-projektu
=====================
Repozytorium: {url}
Student:       {imię nazwisko}
Nr indeksu:    {numer}
Temat:         {temat z README}
Prowadzący:    laugustyniak dodany jako collaborator

Pliki:
  README.md   — OK
  PROCESS.md  — OK
  wyniki/     — OK ({n} plików)

Status: GOTOWE DO OCENY
```

## Ważne

- Nie pushuj kodu za studenta bez pytania.
- Nie modyfikuj plików studenta — tylko waliduj.
- Odpowiadaj po polsku.