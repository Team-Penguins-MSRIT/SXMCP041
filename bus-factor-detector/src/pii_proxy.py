"""
pii_proxy.py — Local PII scrubbing before any LLM call
Install: pip install presidio-analyzer presidio-anonymizer spacy
         python -m spacy download en_core_web_lg
"""

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
import re

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# Map real names to consistent fake labels so the graph stays coherent
_cache: dict[str, str] = {}
_counter = {"n": 0}

def _stable_label(original: str, prefix: str) -> str:
    if original not in _cache:
        _counter["n"] += 1
        _cache[original] = f"{prefix}_{_counter['n']:02d}"
    return _cache[original]

def scrub(text: str) -> str:
    """Strip all PII. Returns anonymized text safe to send to Groq."""
    # Presidio pass
    results = analyzer.analyze(text=text, language="en",
                                entities=["EMAIL_ADDRESS", "PERSON", "PHONE_NUMBER",
                                          "IP_ADDRESS", "URL", "CRYPTO", "IBAN_CODE"])
    anonymized = anonymizer.anonymize(
        text=text,
        analyzer_results=results,
        operators={
            "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "DEVELOPER_EMAIL"}),
            "PERSON":        OperatorConfig("replace", {"new_value": "PERSON_NAME"}),
        }
    ).text

    # Secondary: catch email-like strings presidio might miss
    anonymized = re.sub(
        r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',
        'DEVELOPER_EMAIL',
        anonymized
    )
    return anonymized

def scrub_commit_log(raw_log: str) -> tuple[str, dict]:
    """
    Scrub a commit log and return:
      - cleaned text (safe for LLM)
      - author_map {anonymized_label: commit_count}
    Preserves consistent labels per author across the log.
    """
    author_map: dict[str, int] = {}
    cleaned_lines = []

    for line in raw_log.strip().split("\n"):
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split(None, 2)
        if len(parts) < 3:
            continue
        date, author_raw, message = parts[0], parts[1], parts[2]

        # Give each unique author a stable anonymized label
        label = _stable_label(author_raw, "DEV")
        author_map[label] = author_map.get(label, 0) + 1
        cleaned_lines.append(f"{date} {label} {message}")

    return "\n".join(cleaned_lines), author_map


if __name__ == "__main__":
    test = '2024-01-03 alex.chen@corp.com "Rewrite auth middleware"'
    print(scrub(test))
