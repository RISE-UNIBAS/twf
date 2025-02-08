Installation Guide
==================

This guide will help you install the necessary software to run TWF in
your own environment. It is meant to be installed on a server and not
on a local machine. This guide assumes you have a basic understanding
of how to use a command line interface and are installing on a Linux
server.

TWF is a Django application and it uses Celery for background tasks.
It uses PostgreSQL as the database. Other types of databases may work,
but they are not officially supported (mainly because of the use of JSON fields).
TWF uses a number of third-party libraries, which are listed in the `requirements.txt`
file in the root of the repository.

.. note::

    - This guide assumes you have a working installation of Python 3.10 or later.
      If you do not, you will need to install it before proceeding.

    - This guide assumes you have a working installation of PostgreSQL. If you do not,
      you will need to install it before proceeding.

    - This guide assumes you have a working installation of Redis. If you do not,
      you will need to install it before proceeding.

    - This guide assumes you have credentials for a google service account with access to the
      google sheets API. If you do not, you will need to create one before proceeding.

    - This guide assumes you have access to an app email account. If you do not, you will need to
      create one before proceeding.


Preparation
-----------
Create a new directory for the TWF installation and change to that directory:

.. code-block:: bash

    mkdir twf
    cd twf

Create a new virtual environment and activate it:

.. code-block:: bash

    python3 -m venv venv
    source venv/bin/activate

Clone the TWF repository:

.. code-block:: bash

    git clone https://github.com/RISE-UNIBAS/twf.git

Change to the TWF directory:

.. code-block:: bash

    cd twf

Install the required Python packages:

.. code-block:: bash

    pip install -r requirements.txt

Create a new PostgreSQL database and user:

.. code-block:: bash

    sudo -u postgres psql
    CREATE DATABASE twf;
    CREATE USER
    twf WITH PASSWORD 'password';
    GRANT ALL PRIVILEGES ON DATABASE twf TO twf;
    \q

Create a new Redis database and enable it:

.. code-block:: bash

    sudo apt-get install redis-server
    sudo systemctl enable redis-server


Configuration
-------------
Adjust transkribusWorkflow/settings.py to match your environment. The most important settings are:

- `SECRET_KEY`: A random string used to secure the application. You can generate one using `python -c 'import secrets; print(secrets.token_urlsafe(50))'`.
- `DEBUG`: Set to `False` in production.
- `ALLOWED_HOSTS`: A list of hostnames that the application is allowed to run on.
- `DATABASES`: The database configuration. You will need to adjust the `USER`, `PASSWORD`, and `HOST` settings.
- `CELERY_BROKER_URL`: The URL of the Redis server.
- `CELERY_RESULT_BACKEND`: The URL of the Redis server.

Run the migrations and collect the static files:

.. code-block:: bash

    python manage.py migrate
    python manage.py collectstatic

(You might also need to create a `media` directory in the root of the project)

Create a superuser:

.. code-block:: bash

    python manage.py createsuperuser

Start the Celery worker:

.. code-block:: bash

    celery -A transkribusWorkflow worker -l info

Start the Django development server:

.. code-block:: bash

    python manage.py runserver


Notes on Deployment
-------------------
This guide is meant to get you up and running quickly. For a production
deployment, you will need to use a more robust setup. This includes
using a WSGI server like Gunicorn, a reverse proxy like Nginx, and a
process manager like Supervisor. You will also need to set up HTTPS
using a service like Let's Encrypt.

