import json
import random
import sys
import time

from kafka import KafkaProducer

if len(sys.argv) != 4:
    print("Usage: python producer.py <province_name> <typical_temperature> <typical_humidity>")
    sys.exit(1)

province = sys.argv[1]

try:
    typical_temperature = float(sys.argv[2])
    typical_humidity = float(sys.argv[3])
except ValueError:
    print("Error: temperature and humidity must be numbers")
    sys.exit(1)

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

last_temperature = typical_temperature
last_humidity = typical_humidity

while True:
    temperature = round(random.normalvariate(last_temperature, 0.2), 2)
    temperature = max(10, min(40, temperature))
    last_temperature = temperature

    humidity = round(random.normalvariate(last_humidity, 1), 2)
    humidity = max(0, min(100, humidity))
    last_humidity = humidity

    temperature_reading = {
        "location": province,
        "value": temperature,
        "timestamp": time.time(),
    }
    producer.send("temperature", temperature_reading)
    print("Enviado temperatura:", temperature_reading)

    humidity_reading = {
        "location": province,
        "value": humidity,
        "timestamp": time.time(),
    }
    producer.send("humidity", humidity_reading)
    print("Enviado humedad:", humidity_reading)

    time.sleep(1)
