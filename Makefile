all: migrate run

mig:
	python3 manage.py makemigrations
	python3 manage.py migrate

run:
	python3 manage.py runserver 0:8000
