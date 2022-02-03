set -e

python manage.py migrate
python manage.py update_index
