#!/bin/bash
# LE CROCHET DE DÉMARRAGE D'UNE SESSION CLOUD (le client, le 23/10/2026 :
# « installe playwright cli pour le projet »). Le conteneur est neuf à
# chaque session : ce qui n'est pas dans le dépôt est à refaire.
#  1. le crochet git du dépôt (CLAUDE.md : « dans un conteneur neuf,
#     git config core.hooksPath .githooks d'abord » — le 26/09/2026, un
#     commit est passé avec verifier-depot.py à 1, faute de crochet) ;
#  2. playwright-cli, version épinglée : le skill .claude/skills/playwright-cli
#     a été relu pour CETTE version ; en changer, c'est le relire ;
#  3. sa configuration, vers le Chromium du conteneur : jamais
#     « playwright install », le navigateur est déjà là.
# Hors du cloud, rien : le poste de chacun a sa propre installation.
# Un échec n'empêche pas la session de démarrer ; il est dit.
set -uo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0

git config core.hooksPath .githooks || echo "crochet git : impossible de régler core.hooksPath" >&2

VERSION=0.1.22
if [ "$(playwright-cli --version 2>/dev/null)" != "$VERSION" ]; then
  npm install -g "@playwright/cli@$VERSION" >/dev/null 2>&1 \
    || echo "playwright-cli $VERSION : installation impossible (réseau ?)" >&2
fi

if [ -x /opt/pw-browsers/chromium ]; then
  mkdir -p .playwright
  cat > .playwright/cli.config.json <<'JSON'
{"browser":{"browserName":"chromium","launchOptions":{"executablePath":"/opt/pw-browsers/chromium","headless":true}}}
JSON
fi
exit 0
