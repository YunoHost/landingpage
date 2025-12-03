# YunoHost landingpage

## How to contribute

The landingpage is built thanks to [Astro](https://astro.build).

!! Please do not edit directly `dist/index.*.html` files

1. `export LANDINGPAGE_DEV=true`
2. Run `bash bin/regenerate.sh`
3. Make your change inside `index.html` and others files (image, CSS, translations)
4. Rerun `bash bin/regenerate.sh`

To speed up things, you can run `bash bin/regenerate.sh html` if you change HTML or CSS things, and `bash bin/regenerate.sh i18n` to recompile translations.
