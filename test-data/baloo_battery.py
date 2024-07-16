import paho.mqtt.client as mqtt
import json
import copy

battery_clientid = "bt001"
battery_registration = {
  "clientId": battery_clientid,
  "productId": 41904,
  "connected": 1,
  "version": "v0.1",
  "services": {
    "bt1": "battery"
  }
}
battery_unregister = copy.deepcopy(battery_registration)
battery_unregister["connected"] = 0
battery_data = {
    "Dc/0/Voltage": 14.22,
    "Dc/0/Current" : 5.5,
    "Dc/0/Power" : 5.5,
    "Dc/0/Temperature": 24,
    "Dc/1/Voltage": 12.72,
    "Soc": 89
}

def on_connect_battery(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("device/{}/DBus".format(battery_clientid))
    client.publish("device/{}/Status".format(battery_clientid), json.dumps(battery_registration))

def on_message_battery(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    dbus_msg = json.loads(msg.payload)
    portalId = dbus_msg.get("portalId")

    deviceId = dbus_msg.get("deviceInstance").get("bt1") # UPDATE THIS
    if (deviceId is not None):
      for key in battery_data:
          topic = "W/{}/battery/{}/{}".format(portalId, deviceId, key) # UPDATE THIS
          print("{} = {}".format(topic, battery_data.get(key) ) )
          client.publish(topic, json.dumps({ "value": battery_data.get(key) }) )

client_battery = mqtt.Client()
client_battery.on_connect = on_connect_battery
client_battery.on_message = on_message_battery
client_battery.will_set("device/{}/Status".format(battery_clientid), json.dumps(battery_unregister)) # UPDATE THIS
client_battery.connect("venus.local", 1883, 60)
client_battery.loop_forever()

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

