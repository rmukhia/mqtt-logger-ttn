from paho.mqtt import client as paho_client
from pymongo import MongoClient as mongo_client
import json
import os
from os.path import join, dirname
from dotenv import load_dotenv

mqtt_client = None


def on_connect(_client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code {}\n".format(rc))

    topic_fmt = os.environ.get("MQTT_TOPIC")
    topic = topic_fmt + 'up'
    print("Subscribed to {}".format(topic))
    mqtt_client.subscribe(topic)

    topic = topic_fmt + 'down/+'
    print("Subscribed to {}".format(topic))
    mqtt_client.subscribe(topic)


def on_message(_client, coll, msg):
    msg_json = json.loads(msg.payload.decode())
    data_id = coll.insert_one(msg_json).inserted_id
    print("inserted {}".format(data_id))


if __name__ == '__main__':
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    db_user = os.environ.get('MONGO_USER')
    db_password = os.environ.get('MONGO_PASS')
    db_host = 'mongodb://{}:{}@mongo'.format(db_user, db_password)
    print("Connecting to ", db_host)
    db_client = mongo_client(db_host)

    collection = db_client['lora-stability']['data']

    mqtt_client = paho_client.Client(os.environ.get("MQTT_CLIENT_ID"))
    mqtt_client.username_pw_set(os.environ.get("MQTT_USERNAME"), os.environ.get("MQTT_PASSWORD"))
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.user_data_set(collection)
    mqtt_client.connect(os.environ.get("MQTT_BROKER"), int(os.environ.get("MQTT_PORT")))

    mqtt_client.loop_forever()
