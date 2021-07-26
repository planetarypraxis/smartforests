set -e

pipenv install
yarn

if [ "$SKIP_MIGRATE" != "1" ]; then
  pipenv run python manage.py migrate
  pipenv run python manage.py preseed_transfer_table auth wagtailcore wagtailimages.image wagtaildocs search home smartforests
  pipenv run python manage.py createsuperuser
  touch smartforests/settings/local.py
fi
