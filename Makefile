# postgres
create-db:
	psql -U postgres -c "CREATE DATABASE web_comments;"

recreate-schema:
	psql -U postgres -d $(dbname) -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;'


# django
run-server:
	python src/manage.py runserver $(port)

migrate:
	python src/manage.py migrate $(app)

make-migrations:
	python src/manage.py makemigrations $(app)

create-superuser:
	python src/manage.py createsuperuser --noinput
