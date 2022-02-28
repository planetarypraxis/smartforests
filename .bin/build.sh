set -e

yarn build
rm -rf node_modules

if [ -z "$MEDIA_URL" ]; then
    echo "MEDIA_URL environment variable is blank, setting to https://smartforests.ams3.cdn.digitaloceanspaces.com/"
    export MEDIA_URL=https://smartforests.ams3.cdn.digitaloceanspaces.com/
fi

SKIP_DB=1 SECRET_KEY=dummy python manage.py collectstatic --noinput --clear
