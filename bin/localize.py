import yaml
import os
from jinja2 import Environment, FileSystemLoader

LOCALES_PATH = "locales"
TEMPLATES_PATH = "./"
DIST_PATH = "dist"
DEFAULT_LOCALE = "en"

# Find supported locales
locales = [file.replace('.yaml', '') for file in os.listdir(LOCALES_PATH)]

# Load default locale
with open(f"{LOCALES_PATH}/{DEFAULT_LOCALE}.yaml") as default_locale_file:
    default_text = yaml.safe_load(default_locale_file)

# Load template
env = Environment(loader=FileSystemLoader(TEMPLATES_PATH))
template = env.get_template("index.html")

# Generate translated html for each locales
for locale in locales:
    with open(f"{LOCALES_PATH}/{locale}.yaml") as locale_file:
        translations = yaml.safe_load(locale_file)

    translated_html = template.render(default_text | translations)

    with open(f"{DIST_PATH}/index.{locale}.html", "w") as file:
        file.write(translated_html)

