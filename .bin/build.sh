set -e

yarn build
rm -rf node_modules
echo "MEDIA_URL set to $MEDIA_URL"
SKIP_DB=1 SECRET_KEY=dummy python manage.py collectstatic --noinput --clear
