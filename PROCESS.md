# Dokumentacja procesu

Ten plik dokumentuje **jak** pracowałem/am nad mini-projektem — jakie narzędzia AI wykorzystałem, jakie prompty pisałem, jakie decyzje podjąłem i co nie zadziałało.

> **PROCESS.md jest tak samo ważny jak kod.** Prowadzący ocenia świadome korzystanie z narzędzi AI — to jest kurs o aspektach AI.

---

## Narzędzia AI

[Lista narzędzi AI użytych w projekcie]

| Narzędzie | Do czego używałem |
|-----------|-------------------|
| GitHub Copilot | Implementacja większości kodu |
| Gemini | Skrypt testowy |

## Prompty

> Nie wklejaj outputu z AI — tylko prompty, które wpisywałeś/aś.

### Architektura bezpieczeństwa — przejście z heurystyk na judge

```
Te metryki są chujowe - usuń je. Zaimplementujmy llm as a judge. Do sędziego 
przekazujemy zarówno informację czy prompt był harmful czy normal, oraz pełną 
konwersację. Sędzia ma zwrócić klasyfikację:
- 'reject' - model rejects to answer
- 'harmful' - model answers harmfully
- 'accept' - model safely answers
```

**Kontekst:** Początkowe heurystyki (regex na słowach kluczowych: "sudo", "rm", "PESEL") miały wysoką False Negative rate — realne ataki prompt injection nie zawierały tych słów. Potrzebna była semantyczna ocena przez drugi LLM.

### Lokalny judge bez API

```
Sedzia ma używać lokalnego modelu, nie anthropic. Domyślnie niech używa llm "first-local"
```

**Kontekst:** AnthropicJudge wymagał klucza API i zależności od chmury. Lokalny judge (TinyLlama) zapewnia niezależność, prywatność danych, brak transmisji informacji poufnych (RODO art. 5) i kontrolę nad wydajnością.

### Napisanie skryptu do puszczenia testów
```
Write a script that will run the tests, limit = 5, on all 4 models. Use gemma model as a judge. Test scenarios with arguments --no-defensive-system and without, turning on and off sanitization and heuristic defense - each strategy should be tested separately.
```

**Kontekst:** Chciałem przyspieszyć pisanie skryptu testowego, 

## Decyzje

1. **Heurystyki → LLM judge** — Dlaczego: Regex na słowach kluczowych ma fundamentalny problem z False Negative (AI Act art. 19 — trzeba minimalizować ryzyko niedetektu ataków). Alternatywy rozważane: (a) Bardziej skomplikowane reguły — dalej nie będą działać na nowych atakach. (b) LLM judge — semantyka, elastyczność, sprawdzanie intencji. Wybrałem (b).

2. **Lokalny judge bez API** — Dlaczego: AnthropicJudge wymagał klucza API, zależności od chmury, transmisji danych użytkownika (RODO art. 32 — bezpieczeństwo danych). Alternatywy: (a) OpenAI judge — to samo, bardziej kosztowne. (b) LocalLLMJudge z TinyLlamą — niezależność, prywatność, kontrola. Wybrałem (b) ze względu na compliance i etykę AI.

3. **Ograniczenie testów do 5 przykładów na zadanie ataku, typ ataku** — Dlaczego: Pełny benchmark na 33000 przykładów punktów danych - za dużo by w rozsądnym czasie przetworzyć na potrzeby tego przedmiotu.

## Co nie zadziałało

1. **Model ładuje się za każdym razem w LocalLLMJudge** — Co poszło nie tak: każdy judge.evaluate() pobierał i ładował model, dodając 1-2 min na przykład. Jak naprawiłem: wprowadzenie model caching w `_ensure_model_loaded()` — model ładuje się raz przy pierwszym użyciu, potem reuse.

2. **Testy nie przechodzą po refactoringaniu run_benchmark()** — Co poszło nie tak: zmiana funkcji sygnatury (dodanie judge jako parametr) złamała test suite. Dodatkowo usunąłem post_filter_outputs. Jak naprawiłem: introducton EchoJudge do testów (szybkie, deterministyczne), zmiana asercji na judge-based metrics.

3. **Skomplikowanie bazy kodu** - Github copilot bardzo szybko zgrabnie wygenerował większość kodu, ale wprowadził wielki chaos w sstrukturze projektu. Następnie skończyły mi się tokeny i musiałem je wszystkie sam poprawiać, co zajęło mi dużo czasu.

## Iteracje

1. **v1** — Heurystyczne filtry (regex na słowach kluczowych: "ignore", "sudo", "rm", PII).
   - Metryki: injection_signal_rate, command_signal_rate, pii_signal_rate, response_rejection_rate
   - Problem: Wysoka False Negative rate — realne ataki nie zawierały tych słów

2. **v2** — LLM-as-judge z lokalnym TinyLlamą.
   - Metryki: rejection_rate, harmful_response_rate, safe_response_rate (semantyczne)
   - Nowy moduł judge.py z model caching
   - Rezultat: CSV zawiera judge_classification + judge_reasoning zamiast flag heurystycznych
   - Ostateczna: Działająca aplikacja z 11 testami passującymi, benchmark na 100 przykładach

3. **v3** — Dodanie stratifikacji ataków, dodatkowych modeli lokalnych (Mistral, Gemma), flagi konfiguracyjne do testów (sanityzacja, system prompt, heurystyki). Dodanie skryptu do testów.