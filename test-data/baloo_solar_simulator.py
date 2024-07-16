import paho.mqtt.client as mqtt
import json
import copy

solar_clientid = "ss001"
solar_registration = {
  "clientId": solar_clientid,
  "productId": 41045,
  "connected": 1,
  "version": "v0.1",
  "services": {
    "ss1": "solarcharger"
  }
}
solar_unregister = copy.deepcopy(solar_registration)
solar_unregister["connected"] = 0
solar_data = {
    "State": 4,
    "Dc/0/Voltage": 13.22,
    "Dc/0/Current" : 5.1,
    "Yield/System": 1100,
    "Load/I": 15,
    "Pv/0/P": 8,
    "Pv/0/Name": "Pannello 1"
}

def on_connect_solar(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("device/{}/DBus".format(solar_clientid))
    client.publish("device/{}/Status".format(solar_clientid), json.dumps(solar_registration))

# The callback for when a PUBLISH message is received from the server.
def on_message_solar(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    dbus_msg = json.loads(msg.payload)
    portalId = dbus_msg.get("portalId")

    deviceId = dbus_msg.get("deviceInstance").get("ss1") # UPDATE THIS
    print(str(deviceId))
    if (deviceId is not None):
      for key in solar_data:
          topic = "W/{}/solarcharger/{}/{}".format(portalId, deviceId, key) # UPDATE THIS
          print("{} = {}".format(topic, solar_data.get(key) ) )
          client.publish(topic, json.dumps({ "value": solar_data.get(key) }) )

client_solar = mqtt.Client()
client_solar.on_connect = on_connect_solar
client_solar.on_message = on_message_solar
client_solar.will_set("device/{}/Status".format(solar_clientid), json.dumps(solar_unregister)) # UPDATE THIS
client_solar.connect("venus.local", 1883, 60)
client_solar.loop_forever()

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

