#!/usr/bin/env python3

import os
import argparse
import re
import requests
import json
from langcodes import Language
from pathlib import Path

import markdown
from babel.support import Translations
from jinja2 import Environment, FileSystemLoader


LANDINGPAGE_DIR = Path(__file__).resolve().parent.parent
LOCALES_PATH = LANDINGPAGE_DIR / "translations"
TEMPLATES_PATH = LANDINGPAGE_DIR
DEV = bool(os.environ.get("LANDINGPAGE_DEV"))

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "output",
        type=Path,
        nargs="?",
        default=LANDINGPAGE_DIR / "dist",
        help="Output directory of assets and generated HTMLs",
    )
    args = parser.parse_args()

    def no_p(non_p_string: str) -> str:
        """Strip enclosing paragraph marks, <p> ... </p>,
        which markdown() forces, and which interfere with some jinja2 layout
        """
        return re.sub("(^<P>|</P>$)", "", non_p_string, flags=re.IGNORECASE)

    def cycling(value: str) -> str:
        div_start = (
            '<span class="cycling-words inline-block text-left whitespace-nowrap">'
        )
        div_stop = "</span>"
        span_start = '<span class="bg-gray-100 dark:bg-[#2A2D2E]">'
        span_stop = "</span>"
        return (
            value.replace("%(", f"{div_start}{span_start}")
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
    template_donate = jinja_env.get_template("donate.html")

    # Load blog data
    with open("blog.json", "r") as file:
        data = json.load(file)
    articles = [
        {
            "title": article.get("unicode_title", article["title"]),
            "link": f"https://forum.yunohost.org/t/{article['slug']}/{article['id']}",
            "date": article["created_at"],
        }
        for article in data["topic_list"]["topics"]
        if article["visible"]
    ]
    articles.sort(key=lambda item: item["date"], reverse=True)
    articles = articles[0:6]

    # Fetch weblate statistics to list locales translated abode a certain treshold
    j = requests.get(
        "https://translate.yunohost.org/api/components/yunohost/landingpage/statistics/"
    ).json()

    def get_lang_native_name(code):
        return Language.make(language=code).display_name(code).title()

    relevant_langs = {
        lang["code"]: get_lang_native_name(lang["code"])
        for lang in j["results"]
        if lang["translated_percent"] > 50
    }
    relevant_langs = dict(sorted(relevant_langs.items()))

    if DEV:
        relevant_langs = {k:v for k, v in relevant_langs.items() if k in ["en", "fr"]}

    # Generate 'en'
    locale = "en"
    data_for_jinja = {
        "articles": articles,
        "langs": relevant_langs,
        "_": lambda s: s,
        "dev": DEV,
        "tailwind_css": open("assets/css/input.css").read() if DEV else ""
    }
    translated_html = template.render({ "lang": locale, **data_for_jinja })
    with open(f"{args.output}/index.{locale}.html", "w") as file:
        file.write(translated_html)

    translated_donate_html = template_donate.render({ "lang": locale, **data_for_jinja })
    with open(f"{args.output}/donate.{locale}.html", "w") as file:
        file.write(translated_donate_html)

    # Generate translated html for each locales
    locales = [localedir.name for localedir in LOCALES_PATH.iterdir()]
    for locale in locales:
        if locale not in relevant_langs:
            continue
        translations = Translations.load(LOCALES_PATH, [locale])
        jinja_env.install_gettext_translations(translations)  # type: ignore

        translated_html = template.render({ "lang": locale, **data_for_jinja })
        with open(f"{args.output}/index.{locale}.html", "w") as file:
            file.write(translated_html)

        translated_donate_html = template_donate.render({ "lang": locale, **data_for_jinja })
        with open(f"{args.output}/donate.{locale}.html", "w") as file:
            file.write(translated_donate_html)


if __name__ == "__main__":
    main()
