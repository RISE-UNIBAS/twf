Installation Guide
==================

This guide will walk you through the process of setting up a Django project and adding 'twf' as a module to the project. We will also cover how to create a Gunicorn service and serve it over Nginx.

Installing Django and Starting a Project
----------------------------------------

First, you need to install Django. You can do this using pip:

.. code-block:: bash

   pip install django

Once Django is installed, you can create a new project:

.. code-block:: bash

   django-admin startproject myproject

Adding 'twf' as a Module to the Project
---------------------------------------

To add 'twf' as a module to your project, you first need to create a new application within your project:

.. code-block:: bash

   python manage.py startapp twf

Then, add 'twf' to the `INSTALLED_APPS` list in your project's settings:

.. code-block:: python

   INSTALLED_APPS = [
       ...
       'twf',
       ...
   ]

Finally, include the 'twf' URL configuration in your project's `urls.py` file:

.. code-block:: python

   from django.urls import include

   urlpatterns = [
       ...
       path('twf/', include('twf.urls')),
       ...
   ]

Creating a Gunicorn Service
---------------------------

To create a Gunicorn service, first install Gunicorn:

.. code-block:: bash

   pip install gunicorn

Then, create a Gunicorn systemd service file:

.. code-block:: bash

   sudo nano /etc/systemd/system/gunicorn.service

In the service file, add the following:

.. code-block:: ini

   [Unit]
   Description=gunicorn daemon
   After=network.target

   [Service]
   User=sorinmarti
   Group=www-data
   WorkingDirectory=/path/to/your/project
   ExecStart=/path/to/your/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/path/to/your/project.sock myproject.wsgi:application

   [Install]
   WantedBy=multi-user.target

Replace `/path/to/your/project` and `/path/to/your/venv` with the actual paths to your project and virtual environment.

Serving the Application Over Nginx
----------------------------------

First, install Nginx:

.. code-block:: bash

   sudo apt-get install nginx

Then, create a new Nginx server block configuration:

.. code-block:: bash

   sudo nano /etc/nginx/sites-available/myproject

In the server block configuration, add the following:

.. code-block:: nginx

   server {
       listen 80;
       server_name your_domain www.your_domain;

       location = /favicon.ico { access_log off; log_not_found off; }
       location /static/ {
           root /path/to/your/project;
       }

       location / {
           include proxy_params;
           proxy_pass http://unix:/path/to/your/project.sock;
       }
   }

Replace `your_domain` with your actual domain, and `/path/to/your/project` with the actual path to your project.

Finally, enable the Nginx server block configuration:

.. code-block:: bash

   sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled
   sudo nginx -t
   sudo service nginx restart
