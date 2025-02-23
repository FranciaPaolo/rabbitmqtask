import time
import pika
import pika.spec
import json

import pika.adapters.blocking_connection
import pika.delivery_mode


def update_product(message):
    """Update product in database"""
    # Update product in database

    # raise Exception("Product not found")
    return f"Product {message['product_id']} updated successfully"

def callback(ch:pika.adapters.blocking_connection.BlockingChannel, method:pika.spec.Basic.Deliver, properties:pika.BasicProperties, body:any, queue_name:str):
    """Process the message and send a response back to RabbitMQ"""
    message = json.loads(body)
    print(f" [→] Received from {queue_name}: {message}")

    result_obj={ "success": True, "message": ""}
    try:

        if queue_name == 'update_product_queue':
            result_obj["message"] = update_product(message)
        else:
            result_obj["message"] = "Invalid queue"
    except Exception as e:
        result_obj["message"] = str(e)
        result_obj["success"]=False
        print(f"Error {e}")

    # Publish result to reply queue
    ch.basic_publish(
        exchange='',
        routing_key=properties.reply_to,
        body=json.dumps(result_obj),
        properties=pika.BasicProperties(delivery_mode=2)
    )

    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(f" [→] Processed from {queue_name}: {message} -> Success: {result_obj['success']}")

def start_consumer(queue_name):
    """Start RabbitMQ consumer"""
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)

    channel.basic_consume(queue=queue_name,
                          on_message_callback=lambda ch, method, properties, body: callback(ch, method, properties, body, queue_name),
                          auto_ack=False)

    print(f" [*] Listening to {queue_name}...")
    channel.start_consuming()

import threading

# Start consumers in separate threads
threading.Thread(target=start_consumer, args=('update_product_queue',), daemon=True).start()
#threading.Thread(target=start_consumer, args=('add_product_queue',), daemon=True).start()

while True:
     pass