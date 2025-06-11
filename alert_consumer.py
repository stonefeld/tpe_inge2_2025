import json
import sys
from datetime import datetime

from kafka import KafkaConsumer

if len(sys.argv) != 5:
    print("Usage: python alert_consumer.py <province> <temperature_threshold> <humidity_threshold> <alert_type>")
    print("alert_type can be 'above' or 'below'")
    sys.exit(1)

province = sys.argv[1]

try:
    temp_threshold = float(sys.argv[2])
    humidity_threshold = float(sys.argv[3])
except ValueError:
    print("Error: temperature and humidity thresholds must be numbers")
    sys.exit(1)

alert_type = sys.argv[4].lower()
if alert_type not in ["above", "below"]:
    print("Error: alert_type must be 'above' or 'below'")
    sys.exit(1)

consumer = KafkaConsumer(
    "temperature",
    "humidity",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="earliest",
)

print(f"Monitoring {province} for {alert_type} thresholds:")
print(f"Temperature threshold: {temp_threshold}°C")
print(f"Humidity threshold: {humidity_threshold}%")
print("-" * 50)

for msg in consumer:
    data = msg.value
    if data["location"] != province:
        continue

    value = float(data["value"])
    topic = msg.topic
    timestamp = datetime.fromtimestamp(data["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")

    if topic == "temperature":
        if (alert_type == "above" and value > temp_threshold) or (alert_type == "below" and value < temp_threshold):
            print(f"[{timestamp}] 🚨 ALERTA DE TEMPERATURA: {province} {alert_type} {temp_threshold}°C (actual: {value:.1f}°C)")
    else:
        if (alert_type == "above" and value > humidity_threshold) or (alert_type == "below" and value < humidity_threshold):
            print(f"[{timestamp}] 💧 ALERTA DE HUMEDAD: {province} {alert_type} {humidity_threshold}% (actual: {value:.1f}%)")
