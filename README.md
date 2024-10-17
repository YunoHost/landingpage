# Yunohost landingpage

## How to contribute
!! Please do not edit directly index.*.html files

```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
bash bin/fetch_assets
```

Make your change inside `index.html` view


## Translations

It's based on Flask-Babel : https://python-babel.github.io/flask-babel/
```
source venv/bin/activate

# Extract the english sentences from the code, needed if you modified it
pybabel extract -F babel.cfg -o messages.pot index.html

# If working on a new locale: initialize it (in this example: fr)
pybabel init -i messages.pot -d translations -l fr
# Otherwise, update the existing .po:
pybabel update -i messages.pot -d translations

# ... translate stuff in translations/<lang>/LC_MESSAGES/messages.po
# re-run the 'update' command to let Babel properly format the text
# then compile:
pybabel compile -d translations

# Generate translated html
python3 bin/localize.py
```
## How to deploy

## TODO
- fonts ?
- vrai schema topologie internet
- mettre à jour les screenshots
- responsive
- a11y
- i18n / jinjaification

