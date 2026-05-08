from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def find_section_body(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.strip().lower() == heading.lower():
            start = index + 1
            break
    if start is None:
        return ""

    body_lines = []
    for line in lines[start:]:
        if line.startswith("## ") or line.startswith("### "):
            break
        body_lines.append(line)
    return "\n".join(body_lines).strip()


def has_substantive_content(body: str) -> bool:
    return bool(body and any(line.strip() for line in body.splitlines()))


def validate_readme(readme_path: Path) -> list[str]:
    errors = []
    text = read_text(readme_path)

    placeholders = ["[Tytuł mini-projektu]", "[Imię Nazwisko]", "[XXXXXX]"]
    missing = [placeholder for placeholder in placeholders if placeholder in text]
    if missing:
        errors.append(
            "README.md zawiera nieuzupełnione placeholdery: " + ", ".join(missing)
        )

    if not re.search(r"\b\d{6}\b", text):
        errors.append("README.md nie zawiera numeru indeksu (6 cyfr)")

    return errors


def validate_process(process_path: Path) -> list[str]:
    errors = []
    text = read_text(process_path)

    for heading in ["## Narzędzia AI", "## Prompty", "## Decyzje"]:
        body = find_section_body(text, heading)
        if not has_substantive_content(body):
            errors.append(f"PROCESS.md: sekcja '{heading}' jest pusta")

    return errors


def validate_results(results_dir: Path) -> list[str]:
    files = [path for path in results_dir.rglob("*") if path.is_file() and path.name != ".gitkeep"]
    if not files:
        return ["Katalog wyniki/ nie zawiera żadnych plików"]
    return []


def validate_custom_code(repo_root: Path) -> list[str]:
    src_files = [path for path in (repo_root / "src").glob("**/*") if path.is_file()]
    notebook_files = [path for path in (repo_root / "notebooks").glob("**/*") if path.is_file()]

    custom_src = [path for path in src_files if path.name not in {"example_openai.py", "example_anthropic.py", "example_gemini.py"}]
    custom_notebooks = [path for path in notebook_files if path.suffix == ".ipynb"]

    if not custom_src and not custom_notebooks:
        return ["Brak własnego kodu w src/ lub notebooks/"]
    return []


def main() -> int:
    errors: list[str] = []

    readme_path = REPO_ROOT / "README.md"
    process_path = REPO_ROOT / "PROCESS.md"
    results_dir = REPO_ROOT / "wyniki"

    if readme_path.exists():
        errors.extend(validate_readme(readme_path))
    else:
        errors.append("Brakuje README.md")

    if process_path.exists():
        errors.extend(validate_process(process_path))
    else:
        errors.append("Brakuje PROCESS.md")

    if results_dir.exists():
        errors.extend(validate_results(results_dir))
    else:
        errors.append("Brakuje katalogu wyniki/")

    errors.extend(validate_custom_code(REPO_ROOT))

    if errors:
        for error in errors:
            print(error)
        return 1

    print("Walidacja zakończona powodzeniem")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
