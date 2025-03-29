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

    def get_color_vars(c: list[int]):
        factor = (100 - c[2]) / 1.5

        def hsl(c: list[int], ld: float):
            return f"hsl({c[0]}, {c[1]}%, {min(c[2] + ld, 100)}%)"

        return " ".join(
            [
                f"--{s}: {hsl(c, i * factor)};"
                for i, s in enumerate(
                    ["color", "item-color", "wireframe-color", "wireframe-item-color"]
                )
            ]
        )

    # Load template
    jinja_env = Environment(loader=FileSystemLoader(TEMPLATES_PATH))
    jinja_env.add_extension("jinja2.ext.i18n")
    jinja_env.filters["markdown"] = markdown.markdown
    jinja_env.filters["no_p"] = no_p
    jinja_env.filters["cycling"] = cycling
    jinja_env.filters["get_color_vars"] = get_color_vars
    template = jinja_env.get_template("index.html")
    template_donate = jinja_env.get_template("donate.html")
    template_roadmap = jinja_env.get_template("roadmap.html")

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

    # Load roadmap data
    roadmap_data = json.loads(Path("roadmap.json").read_bytes())

    def get_lang_native_name(code):
        return Language.make(language=code).display_name(code).title()

    if DEV:
        relevant_langs = {k:get_lang_native_name(k) for k in ["en", "fr"]}
    else:
        # Fetch weblate statistics to list locales translated abode a certain treshold
        j = requests.get(
            "https://translate.yunohost.org/api/components/yunohost/landingpage/statistics/"
        ).json()

        relevant_langs = {
            lang["code"]: get_lang_native_name(lang["code"])
            for lang in j["results"]
            if lang["translated_percent"] > 50
        }

        relevant_langs = dict(sorted(relevant_langs.items()))

    # Generate 'en'
    locale = "en"
    data_for_jinja = {
        "articles": articles,
        "roadmap": roadmap_data,
        "langs": relevant_langs,
        "dev": DEV,
        "tailwind_css": open("assets/css/input.css").read() if DEV else ""
    }
    translated_html = template.render({ "lang": locale, "_": lambda s: s, **data_for_jinja })
    with open(f"{args.output}/index.{locale}.html", "w") as file:
        file.write(translated_html)

    translated_donate_html = template_donate.render({ "lang": locale, "_": lambda s: s, **data_for_jinja })
    with open(f"{args.output}/donate.{locale}.html", "w") as file:
        file.write(translated_donate_html)

    translated_roadmap_html = template_roadmap.render({ "lang": locale, "_": lambda s: s, **data_for_jinja })
    with open(f"{args.output}/roadmap.{locale}.html", "w") as file:
        file.write(translated_roadmap_html)

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

        translated_roadmap_html = template_roadmap.render({ "lang": locale, **data_for_jinja })
        with open(f"{args.output}/roadmap.{locale}.html", "w") as file:
            file.write(translated_roadmap_html)


if __name__ == "__main__":
    main()
