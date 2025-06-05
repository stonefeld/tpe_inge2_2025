import json
import random
import time
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

locations = ["Buenos Aires", "Cordoba", "Mendoza", "Salta"]

# Valores típicos iniciales para cada ciudad
typical_temperatures = {
    "Buenos Aires": 22.0,
    "Cordoba": 25.0,
    "Mendoza": 20.0,
    "Salta": 18.0,
}
typical_humidity = {
    "Buenos Aires": 70.0,
    "Cordoba": 60.0,
    "Mendoza": 50.0,
    "Salta": 55.0,
}

last_temperatures = typical_temperatures.copy()
last_humidity = typical_humidity.copy()

while True:
    for location in locations:
        temperature = round(random.normalvariate(last_temperatures[location], 0.2), 2)
        temperature = max(10, min(40, temperature))
        last_temperatures[location] = temperature

        humidity = round(random.normalvariate(last_humidity[location], 1), 2)
        humidity = max(0, min(100, humidity))
        last_humidity[location] = humidity

        reading = {
            "location": location,
            "temperature": temperature,
            "humidity": humidity,
            "timestamp": time.time(),
        }

        producer.send("iot-temperature", reading)
        print("Enviado:", reading)

    time.sleep(1)
