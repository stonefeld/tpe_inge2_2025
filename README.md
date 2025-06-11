<h1 align="center">Ingeniería del Software II</h1>
<h3 align="center">POC: Apache Kafka</h3>
<h4 align="center">Primer cuatrimestre 2025</h4>

# Objetivo del proyecto

Este es una demo a modo de prueba de concepto que demuestra el funcionamiento de
_Apache Kafka_. Para esto planteamos un sistema que registra datos de
**temperatura** y **humedad** en distintas provincias y los envía a topics de
Kafka. Estos datos luego son consumidos por diferentes _consumers_. El proyecto
consiste en construir una pequeña arquitectura utilizando:

* _Apache Kafka_: a modo de plataforma de transmisión de eventos por medio de
arquitectura _pub/sub_.
* _Zookeeper_: a modo de coordinador para registrar datos del topic y elegir la
partición.
* _InfluxDB_: solo utilizado en una de las implementaciones del consumer para
poder guardar los datos leídos de _Kafka_ y luego visualizarlos con _Grafana_.
* _Grafana_: lo utilizamos para generar gráficos en tiempo real de lo que se
guarda en _InfluxDB_ de los datos tomados del topic de _Kafka_.

Para esto, diseñamos 3 scripts en Python que simulan diferentes entidades:

* `producer.py`: Simula la lectura de un sensor particular en una provincia
especificada. Se le especifican valores típicos de temperatura y humedad para la
provincia para simular una distribución _cercano a lo real_.
* `consumer.py`: Es un consumidor que se subscribe a los topics de Kafka y
guarda los datos leídos en la base de datos de _InfluxDB_. Esos datos están
pensados para poder ser [graficados en _Grafana_](#influxdb-y-grafana-consumer).
* `alert_consumer.py`: Es un consumidor al que se le especifica una provincia a
la que "prestará atención" y se le configuran valores de temperatura y humedad
y emite una alerta si los valores leídos de Kafka están por encima (o por
debajo si se lo especifica al _script_).

# Requisitos

* **Python:** El proyecto utiliza el toolchain de
[`uv`](https://docs.astral.sh/uv/getting-started/installation/). Aunque también
puede correrse directo con Python versión `3.12.9`
* **Docker**
* **Docker compose**

# Instalando las dependencias

Si se está utilizando `uv` como toolchain, correr los siguientes comandos dentro
del repositorio:

```bash
# Para crear y activar el entorno virtual
uv venv    # Esto también instala la versión de Python necesaria
source .venv/bin/activate  # En Unix
.venv\Scripts\activate     # En Windows

# Para instalar las dependencias
uv sync
```

# Levantando la arquitectura

Utilizando `docker-compose` podemos levantar la arquitectura mencionada en la
introducción.

```bash
# Primero, para persistir las configuraciones de Grafana
docker volume create grafana-data

# Ahora si, podemos levantar la arquitectura
docker compose up --build -d
```

Esto levantará los siguientes contenedores:

| Contenedor | Puertos |
| --- | --- |
| `kafka` | `9092:9092` |
| `zookeeper` | `2181:2181` |
| `influxdb` | `8086:8086` |
| `grafana` | `3000:3000` |

# Corriendo

## Producers

Para correr los producers, se utiliza el script de `producer.py` que espera como
parámetros:

* `province_name`: El nombre de la provincia donde se simula la lectura del
sensor.
* `typical_temperature`: La temperatura típica de la provincia, para simular
variaciones de temperatura cercanos a la realidad.
* `typical_humidity`: Idem anterior, pero con la humedad típica de la provincia.

Entonces, podemos simular la lectura en varias provincias distintas corriendo lo
siguiente:

```bash
uv run producer.py 'Buenos Aires' 23 76
uv run producer.py 'Salta' 35 69
uv run producer.py 'Cordoba' 20 69
uv run producer.py 'Corrientes' 30 80
```

## Consumers

Existen dos consumers diferentes que pueden consumir los datos subscribiéndose a
los topics de Kafka

### InfluxDB y Grafana consumer

Este consumer tiene como objetivo leer los datos de Kafka y guardarlos en
InfluxDB para luego graficarlos en Grafana. Para correr este consumer, se puede
ejecutar los siguiente:

```bash
uv run consumer.py
```

Luego, estos datos se irán guardando en InfluxDB y, para poder visualizarlos en
Grafana tenemos que seguir las siguientes instrucciones:

1. Desde un browser, ir a la URL `http://localhost:3000`
2. Se pedirá un usuario y contraseña los cuáles por `admin` y `admin`
respectivamente.
3. Agregar un _Data Source_ a Grafana para InfluxDB (`http://localhost:3000/connections/datasources`):
    1. Seleccionar "_InfluxDB_"
    2. Para "_Query language_", seleccionar `Flux`
    3. Bajo `HTTP` y `URL` ingresar `http://influxdb:8086`
    4. Bajo "_Basic Auth Details_" ingresar en _User_ y _Password_, `admin` y
       `adminadmin`, respectivamente
    5. Bajo "_InfluxDB Details_"
       * _Organization_: `ar-edu-itba-inge2`
       * _Token_: `admin-token`
       * _Default Bucket_: `sensor-data`
4. Una vez configurado el _Data Source_, crear un nuevo _Dashboard_ para
   _InfluxDB_ y agregar 2 visualizaciones con las siguientes _queries_:

```flux
from(bucket: "sensor-data")
    |> range(start: -24h)
    |> filter(fn: (r) => r._measurement == "temperature")
    |> map(fn: (r) => ({ r with _field: r.ubicacion }))
```

```flux
from(bucket: "sensor-data")
    |> range(start: -24h)
    |> filter(fn: (r) => r._measurement == "humidity")
    |> map(fn: (r) => ({ r with _field: r.ubicacion }))
```

### Alert consumer

Por otro lado, tenemos el consumer que se ocupa de generar alertas en caso de
que una provincia particular alcance un cierto nivel de temperatura o humedad
por arriba (o por debajo). El script `alert_consumer.py` espera los siguientes
parámetros:

* `province`: La provincia a la cual monitoreamos su humedad y temperatura para
emitir la alerta.
* `temperature_threshold`: El límite de temperatura que registra para emitir la
alerta.
* `humidity_threshold`: Idem anterior pero con la humedad.
* `alert_type`: Puede ser `above` o `below`. Lógicamente, si este parámetro es
`above`, emite la alerta cuando los valores son mayores a su límite
especificado. Caso contrario, si es `below`, se emite cuando los valores leídos
están por debajo.

Entonces, si queremos emitir una alerta cuando la temperatura en Buenos Aires es
mayor a 30°C y su humedad mayor a 80%, podemos correr lo siguiente:

```bash
uv run alert_consumer.py 'Buenos Aires' 30 80 above
```

En caso de que se emiten las alertas se verán de la siguiente manera:

```
[2025-06-11 15:30:43] 🚨 ALERTA DE TEMPERATURA: Buenos Aires above 30.0°C (actual: 35.1°C)
[2025-06-11 15:32:54] 💧 ALERTA DE HUMEDAD: Buenos Aires above 80.0% (actual: 90.4%)
```
