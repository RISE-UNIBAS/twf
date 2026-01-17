Transkribus workflow
====================
![pylint score](https://mperlet.github.io/pybadge/badges/8.49.svg)

# Start the environment for local development
This assumes that dependencies are installed and components like Redis are set up. This also assumes that you have already
a running PostgreSQL database.

Activate the virtual environment and start the Redis server. Redis acts as a message broker for Celery tasks.
```bash
source venv/bin/activate
sudo service redis-server start
```

Start the Celery worker to process background tasks.
```bash
celery -A transkribus_workflow worker --loglevel=info
```

This command starts the Celery worker, which listens for tasks and executes them as they are received.

This will keep running in the terminal, so in a new shell, activate the virtual environment again and start django's development server.
```bash
source venv/bin/activate
python manage.py runserver
```



