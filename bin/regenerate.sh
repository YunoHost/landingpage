#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
LANDINGPAGE_DIR="$(dirname "$SCRIPT_DIR")"

cd "$LANDINGPAGE_DIR"
venv=$LANDINGPAGE_DIR/venv
dist=$LANDINGPAGE_DIR/dist

if [ -d "$dist" ]; then
    rm -rf "$dist"
fi
mkdir -p dist

if [ -d "$venv" ]; then
    rm -rf "$venv"
fi

python3 -m venv "$LANDINGPAGE_DIR/venv"

source "$venv/bin/activate"

"$venv/bin/pip" install -r requirements.txt

# Extract the english sentences from the code, needed if you modified it
"$venv/bin/pybabel" extract -F babel.cfg -o messages.pot index.html

# If working on a new locale: initialize it (in this example: fr)
"$venv/bin/pybabel" init -i messages.pot -d translations -l fr
# Otherwise, update the existing .po:
"$venv/bin/pybabel" update -i messages.pot -d translations

# ... translate stuff in translations/<lang>/LC_MESSAGES/messages.po
# re-run the 'update' command to let Babel properly format the text
# then compile:
"$venv/bin/pybabel" compile -d translations

# Generate translated html
"$venv/bin/python3" bin/localize.py

# Generate CSS, fonts etc
bash bin/fetch_assets
