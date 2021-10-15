set -e

yarn build
rm -rf node_modules
SKIP_DB=1 SECRET_KEY=dummy python manage.py collectstatic --noinput --clear
