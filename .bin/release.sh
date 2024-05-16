set -e
 
pipenv run python manage.py migrate
pipenv run python manage.py createcachetable
pipenv run python manage.py collectstatic --noinput
