set -e

#pipenv run python manage.py migrate
#pipenv run python manage.py setup_pages
pipenv run python manage.py createcachetable
pipenv run python manage.py collectstatic --noinput
