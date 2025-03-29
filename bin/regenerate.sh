#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
LANDINGPAGE_DIR="$(dirname "$SCRIPT_DIR")"

LANDINGPAGE_VENV_DIR=$(realpath "${LANDINGPAGE_VENV_DIR:-$LANDINGPAGE_DIR/venv}")
LANDINGPAGE_DIST_DIR=$(realpath "${LANDINGPAGE_DIST_DIR:-$LANDINGPAGE_DIR/dist}")

if [[ "${1:-}" == "dev" ]]
then
    command -v inotifywait &>/dev/null || { echo "You should first run: apt install inotify-tools"; exit; }

    # Clear the dist directory
    mkdir -p "$LANDINGPAGE_DIST_DIR"
    rm -rf "${LANDINGPAGE_DIST_DIR:?}"/*

    LANDINGPAGE_DEV=true python3 bin/localize.py "$LANDINGPAGE_DIST_DIR"
    cp -Rf assets "$LANDINGPAGE_DIST_DIR"
    echo "Now watching for changes in *.html and assets/css/*.css"
    while { inotifywait --quiet -r -e modify *.html assets/css/*.css *.json || true; }
    do
        echo "Regenerating..."
        LANDINGPAGE_DEV=true python3 bin/localize.py "$LANDINGPAGE_DIST_DIR"
        cp -Rf assets "$LANDINGPAGE_DIST_DIR"
    done
    exit
fi

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
    pybabel extract -F babel.cfg -o translations/messages.pot *.html --no-location --omit-header

    # If working on a new locale: initialize it (in this example: fr)
    # pybabel init -i translations/messages.pot -d translations -l fr

    # Otherwise, update the existing .po:
    # This is now done automatically via a weblate extension
    #pybabel update -i translations/messages.pot -d translations

    # ... translate stuff in translations/<lang>/LC_MESSAGES/messages.po
    # re-run the 'update' command to let Babel properly format the text
    # then compile:
    locales=$(find translations/ -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort)
    for locale in $locales
    do
        this_locale_file="translations/$locale/LC_MESSAGES/messages"
        if ! [ -e $this_locale_file.mo ] || [ $this_locale_file.po -nt $this_locale_file.mo ]
        then
            pybabel compile -d translations -l $locale
        fi
    done

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
