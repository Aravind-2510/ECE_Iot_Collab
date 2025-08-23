import network
import urequests
import machine
import time
from dht import DHT11

# ---- WiFi Credentials ----
SSID = "hi"
PASSWORD = "0987654321"

# ---- ThingSpeak API ----

THINGSPEAK_URL = "http://api.thingspeak.com/update"

# ---- Pins ----
dht_pin = machine.Pin(4)  # GPIO2 (D2 on NodeMCU)
dht_sensor = DHT11(dht_pin)

soil_pin = machine.ADC(0)  # A0 pin
relay = machine.Pin(14, machine.Pin.OUT)  # D5 = GPIO14

# ---- Connect WiFi ----
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

print("Connecting to WiFi...")
while not wifi.isconnected():
    time.sleep(1)
print("Connected:", wifi.ifconfig())

# ---- Main Loop ----
while True:
    try:
        # Read sensors
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        hum = dht_sensor.humidity()
        soil = soil_pin.read()

        print("Soil Moisture:", soil)
        print("Temperature:", temp, "°C")
        print("Humidity:", hum, "%")

        # Control Pump
        if soil < 500:   # Adjust threshold after calibration
            relay.value(0)  # Pump ON (active low relay)
            print("Soil dry → Pump ON")
        else:
            relay.value(1)  # Pump OFF
            print("Soil wet → Pump OFF")

        # Send Data to ThingSpeak
        response = urequests.get(
            THINGSPEAK_URL +
            "?api_key=" + API_KEY +
            "&field1=" + str(soil) +
            "&field2=" + str(temp) +
            "&field3=" + str(hum)
        )
        print("ThingSpeak Response:", response.text)
        response.close()

    except Exception as e:
        print("Error:", e)

    time.sleep(20)  # ThingSpeak update interval
