#!/usr/bin/env python3

import argparse
import re
from pathlib import Path

import markdown
from babel.support import Translations
from jinja2 import Environment, FileSystemLoader


LANDINGPAGE_DIR = Path(__file__).resolve().parent.parent
LOCALES_PATH = LANDINGPAGE_DIR / "translations"
TEMPLATES_PATH = LANDINGPAGE_DIR


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path, nargs="?", default=LANDINGPAGE_DIR / "dist", help="Output directory of assets and generated HTMLs")
    args = parser.parse_args()

    def no_p(non_p_string: str) -> str:
        """ Strip enclosing paragraph marks, <p> ... </p>,
            which markdown() forces, and which interfere with some jinja2 layout
        """
        return re.sub("(^<P>|</P>$)", "", non_p_string, flags=re.IGNORECASE)

    def cycling(value: str) -> str:
        div_start = "<div class=\"cycling-words inline-block text-left whitespace-nowrap\">"
        div_stop = "</div>"
        span_start = "<span>"
        span_stop = "</span>"
        return (value
            .replace("%(", f"{div_start}{span_start}")
            .replace("|", f"{span_stop}{span_start}")
            .replace(")%", f"{span_stop}{div_stop}")
        )

    # Load template
    jinja_env = Environment(loader=FileSystemLoader(TEMPLATES_PATH))
    jinja_env.add_extension("jinja2.ext.i18n")
    jinja_env.filters["markdown"] = markdown.markdown
    jinja_env.filters["no_p"] = no_p
    jinja_env.filters["cycling"] = cycling
    template = jinja_env.get_template("index.html")

    # Generate translated html for each locales
    locales = [localedir.name for localedir in LOCALES_PATH.iterdir()]
    for locale in locales:
        translations = Translations.load(LOCALES_PATH, [locale])
        jinja_env.install_gettext_translations(translations)  # type: ignore
        translated_html = template.render({"lang": locale})

        with open(f"{args.output}/index.{locale}.html", "w") as file:
            file.write(translated_html)


if __name__ == "__main__":
    main()
