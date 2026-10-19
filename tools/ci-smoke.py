#!/usr/bin/env python3
"""Contrôles de fumée sans données nominatives dans la sortie CI.

Vérifie seulement la structure publique attendue du JSON d'horaire. Les
identifiants, commentaires et journées ne sont jamais imprimés dans les logs.
"""
import datetime
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEDULE = ROOT / "data" / "horaire-2026.json"
MANIFEST = ROOT / "manifest.webmanifest"
SERVICE_WORKER = ROOT / "sw.js"


def main():
    try:
        with SCHEDULE.open(encoding="utf-8") as f:
            data = json.load(f)
        with MANIFEST.open(encoding="utf-8") as f:
            manifest = json.load(f)
        service_worker = SERVICE_WORKER.read_text(encoding="utf-8")
    except (OSError, UnicodeError, json.JSONDecodeError):
        print("ÉCHEC: le JSON d'horaire est absent ou invalide.")
        return 1

    if not isinstance(manifest, dict) or not isinstance(manifest.get("icons"), list):
        print("ÉCHEC: manifeste PWA invalide ou sans icônes.")
        return 1

    assets = []
    for icon in manifest["icons"]:
        if not isinstance(icon, dict) or not isinstance(icon.get("src"), str):
            print("ÉCHEC: déclaration d'icône invalide dans le manifeste.")
            return 1
        assets.append(icon["src"])
    for shortcut in manifest.get("shortcuts", []):
        if not isinstance(shortcut, dict):
            print("ÉCHEC: raccourci PWA invalide.")
            return 1
        for icon in shortcut.get("icons", []):
            if not isinstance(icon, dict) or not isinstance(icon.get("src"), str):
                print("ÉCHEC: icône de raccourci invalide.")
                return 1
            assets.append(icon["src"])
    missing = [asset for asset in assets if not (ROOT / asset).is_file()]
    if missing:
        print("ÉCHEC: une ou plusieurs icônes du manifeste sont absentes.")
        return 1

    core_match = re.search(r"var\\s+CORE\\s*=\\s*\\[(.*?)\\];", service_worker, re.S)
    if not core_match:
        print("ÉCHEC: liste CORE introuvable dans le service worker.")
        return 1
    core_assets = re.findall(r"""["'](\\./[^"']+)["']""", core_match.group(1))
    if not core_assets:
        print("ÉCHEC: liste CORE vide ou illisible.")
        return 1
    for asset in core_assets:
        target = ROOT / asset.removeprefix("./")
        if not (target.is_file() or target.is_dir()):
            print("ÉCHEC: une ressource déclarée dans le cache initial est absente.")
            return 1

    if not isinstance(data, dict):
        print("ÉCHEC: racine JSON inattendue.")
        return 1
    schedule_year = data.get("year")
    if type(schedule_year) is not int or not 2000 <= schedule_year <= 2100:
        print("ÉCHEC: année d'horaire invalide.")
        return 1

    people = data.get("people")
    if not isinstance(people, list) or not people:
        print("ÉCHEC: liste de personnes absente ou vide.")
        return 1

    ids = set()
    days = 0
    for person in people:
        if not isinstance(person, dict) or not person.get("id") or not isinstance(person.get("cat"), str):
            print("ÉCHEC: structure d'une entrée personne invalide.")
            return 1
        if person["id"] in ids:
            print("ÉCHEC: identifiant personne dupliqué.")
            return 1
        ids.add(person["id"])
        calendar = person.get("d")
        if not isinstance(calendar, dict):
            print("ÉCHEC: calendrier personne absent ou invalide.")
            return 1
        for date_key, entry in calendar.items():
            if not isinstance(date_key, str) or not re.fullmatch(r"\d{4}", date_key):
                print("ÉCHEC: clé de date invalide.")
                return 1
            month, day = int(date_key[:2]), int(date_key[2:])
            try:
                datetime.date(schedule_year, month, day)
            except ValueError:
                print("ÉCHEC: date invalide pour 2026.")
                return 1
            if not isinstance(entry, list) or not all(isinstance(v, str) for v in entry):
                print("ÉCHEC: contenu d'une journée invalide.")
                return 1
            days += 1

    print("OK: JSON valide; %d personnes, %d entrées de journées." % (len(people), days))
    return 0


if __name__ == "__main__":
    sys.exit(main())
