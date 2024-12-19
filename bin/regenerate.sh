#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
LANDINGPAGE_DIR="$(dirname "$SCRIPT_DIR")"

LANDINGPAGE_VENV_DIR=$(realpath "${LANDINGPAGE_VENV_DIR:-$LANDINGPAGE_DIR/venv}")
LANDINGPAGE_DIST_DIR=$(realpath "${LANDINGPAGE_DIST_DIR:-$LANDINGPAGE_DIR/dist}")
if [[ "${1:-}" == "" ]]
then
    # Clear the dist directory
    mkdir -p "$LANDINGPAGE_DIST_DIR"
    rm -rf "${LANDINGPAGE_DIST_DIR:?}"/*

    cd "$LANDINGPAGE_DIR"

    # Update, if needed, the assets
    bash bin/fetch_assets

    # Initialize the venv if it does not exist
    if [ ! -d "$LANDINGPAGE_VENV_DIR" ]; then
        python3 -m venv "$LANDINGPAGE_VENV_DIR"
        "$LANDINGPAGE_VENV_DIR/bin/pip" install -r requirements.txt
    fi
fi

source "$LANDINGPAGE_VENV_DIR/bin/activate"

if [[ "${1:-}" == "" || "${1:-}" == "i18n"  ]]
then

    # Extract the english sentences from the code, needed if you modified it
    pybabel extract -F babel.cfg -o translations/messages.pot index.html

    # If working on a new locale: initialize it (in this example: fr)
    # pybabel init -i translations/messages.pot -d translations -l fr

    # Otherwise, update the existing .po:
    # This is now done automatically via a weblate extension
    #pybabel update -i translations/messages.pot -d translations

    # ... translate stuff in translations/<lang>/LC_MESSAGES/messages.po
    # re-run the 'update' command to let Babel properly format the text
    # then compile:
    pybabel compile -d translations
fi
if [[ "${1:-}" == "" || "${1:-}" == "blog"  ]]
then
    curl -L -s -o "blog.json" "https://forum.yunohost.org/c/announcement/8/none.json"
fi
if [[ "${1:-}" == "" || "${1:-}" == "html" || "${1:-}" == "blog"  ]]
then
    # Generate translated html
    python3 bin/localize.py "$LANDINGPAGE_DIST_DIR"

fi
if [[ "${1:-}" == "" || "${1:-}" == "html"  ]]
then
    # Generate CSS, fonts etc
    cp -Rf assets "$LANDINGPAGE_DIST_DIR"

    ./assets/tailwindcss-linux \
        --config "$LANDINGPAGE_DIR/tailwind.config.js" \
        --content "$LANDINGPAGE_DIST_DIR/*.en.html" \
        --input "$LANDINGPAGE_DIR/assets/css/input.css" \
        --output "$LANDINGPAGE_DIST_DIR/assets/css/prod.min.css"
fi
