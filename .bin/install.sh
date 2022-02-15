set -e

pipenv install
yarn

pipenv run python <<EOL
from nltk import download

download('punkt')
EOL

if [ "$SKIP_MIGRATE" != "1" ]; then
  pipenv run python manage.py migrate
  pipenv run python manage.py setup_pages
  pipenv run python manage.py createsuperuser
  touch smartforests/settings/local.py
fi
