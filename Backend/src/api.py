from contextlib import contextmanager
import time
from typing import Generator, Tuple
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import pika
import json
import uuid

import pika.adapters.blocking_connection

app = FastAPI()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins, you can specify a list of origins instead
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

@contextmanager
def get_rabbitmq_channel() -> Generator[Tuple[pika.BlockingConnection, pika.adapters.blocking_connection.BlockingChannel], None, None]:
    """Get a RabbitMQ channel"""
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    yield connection, channel  # Yield connection and channel

@app.post("/update-product")
async def update_product(data: dict, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())  # Unique task ID for tracking
    data["task_id"] = task_id

    # only for debugging purposes ----------------
    if not hasattr(data, "product_id"):
        data["product_id"]=1
    # -------------------------------------------

    with get_rabbitmq_channel() as (connection, channel):
        # Declare reply queue (exclusive to the API instance)
        reply_queue = f"reply_queue_{task_id}"
        channel.queue_declare(queue=reply_queue, exclusive=True, arguments={"x-expires": 60000})

        # Send message to RabbitMQ
        channel.basic_publish(
            exchange='',
            routing_key='update_product_queue',
            body=json.dumps(data),
            properties=pika.BasicProperties(
                delivery_mode=1,
                reply_to=reply_queue  # Set reply queue
            )
        )
        return StreamingResponse(wait_for_result(channel, task_id, reply_queue), media_type="text/event-stream")

async def wait_for_result(channel:pika.adapters.blocking_connection.BlockingChannel, task_id: str, reply_queue: str):
    """SSE Generator to listen for RabbitMQ replies"""

    data={ "completed":False, "success":False, "message":f"processing task: {task_id}" }
    yield f"data: {data}\n\n"
    print(f"data: {data}\n\n")

    method_frame, header_frame, body = channel.basic_get(queue=reply_queue, auto_ack=True) # returns immediately, even if there is no message
    while not body:
        # time.sleep(1)
        method_frame, header_frame, body = channel.basic_get(queue=reply_queue, auto_ack=True)

    body_obj=json.loads(body)
    data["success"]=body_obj["success"]
    data["message"]=body_obj["message"]
    data["completed"]=True
    if data["success"]:
        yield f"data: {data}\n\n"
    else:
        yield f"event: error\ndata: {data}\n\n"
    print(f"data: {data}\n\n")

    channel.queue_delete(queue=reply_queue)
    channel.connection.close()


if __name__=="__main__":
    print("run uvicorn")
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0",port=8080, reload=True)
