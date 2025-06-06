import json
import os
import re
import spacy
from collections import defaultdict
from tqdm import tqdm

# Load SpaCy NER model
nlp = spacy.load("en_core_web_sm")

# Input/output files
INPUT_FILE = "data/classified_leaks.json"
OUTPUT_FILE = "data/extracted_entities.json"

# Regex patterns
EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
PHONE_REGEX = r"(?:(?:\+?91)|(?:\(\+91\))|(?:0))?[\s-]?[789]\d{9}"
IP_REGEX = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
URL_REGEX = r"https?://(?:www\.)?[a-zA-Z0-9./?=#-_]+"
CRED_REGEX = r'(?i)(username|password|pass|login)[\'":\s]+([a-zA-Z0-9@#$_!%^&*\-+=]+)'


def extract_with_regex(text):
    entities = defaultdict(set)
    entities["emails"].update(re.findall(EMAIL_REGEX, text))
    entities["phones"].update(re.findall(PHONE_REGEX, text))
    entities["ips"].update(re.findall(IP_REGEX, text))
    entities["urls"].update(re.findall(URL_REGEX, text))
    entities["credentials"].update(match[1] for match in re.findall(CRED_REGEX, text))
    return entities


def extract_with_ner(text):
    doc = nlp(text)
    entities = defaultdict(set)
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG", "GPE"]:
            entities[ent.label_.lower()].add(ent.text)
    return entities


def merge_entities(e1, e2):
    for key, val in e2.items():
        e1[key].update(val)
    return e1


def extract_entities():
    if not os.path.exists(INPUT_FILE):
        print(f"[-] Input file not found: {INPUT_FILE}")
        return

    with open(INPUT_FILE, "r") as f:
        leaks = json.load(f)

    output = []

    for entry in tqdm(leaks, desc="[+] Extracting entities"):
        if entry.get("label") != "sensitive":
            continue

        text = entry.get("text", "")
        entity_block = defaultdict(set)

        entity_block = merge_entities(entity_block, extract_with_regex(text))
        entity_block = merge_entities(entity_block, extract_with_ner(text))

        output.append({
            "source": entry.get("source"),
            "subdomain": entry.get("subdomain"),
            "entities": {k: list(v) for k, v in entity_block.items()}
        })

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"[+] Extracted entities saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    extract_entities()
