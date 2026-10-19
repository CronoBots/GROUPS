#!/usr/bin/env python3
"""Contrôles de fumée sans données nominatives dans la sortie CI.

Vérifie seulement la structure publique attendue du JSON d'horaire. Les
identifiants, commentaires et journées ne sont jamais imprimés dans les logs.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEDULE = ROOT / "data" / "horaire-2026.json"


def main():
    try:
        with SCHEDULE.open(encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, UnicodeError, json.JSONDecodeError):
        print("ÉCHEC: le JSON d'horaire est absent ou invalide.")
        return 1

    if not isinstance(data, dict) or data.get("year") != 2026:
        print("ÉCHEC: année ou racine JSON inattendue.")
        return 1

    people = data.get("people")
    if not isinstance(people, list) or not people:
        print("ÉCHEC: liste de personnes absente ou vide.")
        return 1

    days = 0
    for person in people:
        if not isinstance(person, dict) or not person.get("id") or not isinstance(person.get("cat"), str):
            print("ÉCHEC: structure d'une entrée personne invalide.")
            return 1
        calendar = person.get("d")
        if not isinstance(calendar, dict):
            print("ÉCHEC: calendrier personne absent ou invalide.")
            return 1
        for date_key, entry in calendar.items():
            if not isinstance(date_key, str) or not re.fullmatch(r"\d{4}", date_key):
                print("ÉCHEC: clé de date invalide.")
                return 1
            month, day = int(date_key[:2]), int(date_key[2:])
            if not (1 <= month <= 12 and 1 <= day <= 31):
                print("ÉCHEC: date hors limites.")
                return 1
            if not isinstance(entry, list) or not all(isinstance(v, str) for v in entry):
                print("ÉCHEC: contenu d'une journée invalide.")
                return 1
            days += 1

    print("OK: JSON valide; %d personnes, %d entrées de journées." % (len(people), days))
    return 0


if __name__ == "__main__":
    sys.exit(main())
