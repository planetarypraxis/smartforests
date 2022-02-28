set -e

yarn build
rm -rf node_modules

if [ -z "$MEDIA_URL" ]; then
    export MEDIA_URL=https://smartforests.ams3.cdn.digitaloceanspaces.com/
fi

SKIP_DB=1 SECRET_KEY=dummy python manage.py collectstatic --noinput --clear
