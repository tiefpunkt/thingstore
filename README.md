# ThingStore
That thing where things to to store their stuff. An open source numerical data store and visualization interface for the internet of things.

## Deployment
We have deployment instructions in the [wiki](https://github.com/tiefpunkt/thingstore/wiki), currently only for [Heroku](https://github.com/tiefpunkt/thingstore/wiki/Heroku).

## API
ThingStore allows you to read and write to the datastore via an API. Documentation on how to do that it written in the [wiki](https://github.com/tiefpunkt/thingstore/wiki/API).

## Development
ThingStore is written in Python, using Django. For easier database migrations, South is used. These and other requirements are noted in the requirements file `requirements.txt`. When first starting development, create a virtual environment to satisfy these requirements without changing anything on your system:

	virtualenv env
	source env/bin/activate
	pip install -r requirements.txt
	python manage.py syncdb
	python manage.py migrate

As last step, start the local development server using ./manage.py runserver and point your browser to http://127.0.0.1:8000.



