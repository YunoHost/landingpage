import yaml
import os
from jinja2 import Environment, FileSystemLoader
from babel.support import Translations

LOCALES_PATH = "translations"
TEMPLATES_PATH = "./"
DIST_PATH = "dist"
DEFAULT_LOCALE = "en"

# Find supported locales
locales = [file for file in os.listdir(LOCALES_PATH)]

# Load template
env = Environment(
    extensions=['jinja2.ext.i18n'],
    loader=FileSystemLoader(TEMPLATES_PATH))
template = env.get_template("index.html")

# Generate translated html for each locales
for locale in locales:
    translations = Translations.load(LOCALES_PATH, [locale])
    env.install_gettext_translations(translations)
    translated_html = template.render({"lang": locale})

    with open(f"{DIST_PATH}/index.{locale}.html", "w") as file:
        file.write(translated_html)

