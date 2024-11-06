# YunoHost landingpage

## How to contribute
!! Please do not edit directly `dist/index.*.html` files

1. Run `bash bin/regenerate.sh`
2. Make your change inside `index.html` and others files (image, CSS, translations)
3. Rerun `bash bin/regenerate.sh`

To speed up things, you can run `bash bin/regenerate.sh html` if you change HTML or CSS things, and `bash bin/regenerate.sh i18n` to recompile translations. 
