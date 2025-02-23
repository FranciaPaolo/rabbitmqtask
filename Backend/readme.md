## Backend components

* Api that expose a post
* Worker that run the task from the queue

## How to start

* Start RabbitMq using the compose `docker compose -f ./docker-compose.yml -p rabbitmq up -d`
* Create the virtual environment `conda create -p venv python=3.10` and activate it `conda activate ./venv`
* Start the Api `python ./src/api.py`
* Start the Worker `python ./src/worker.py`
