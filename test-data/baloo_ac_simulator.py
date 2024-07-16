import paho.mqtt.client as mqtt
import json
import copy

ac_clientid = "ac001"
ac_registration = {
  "clientId": ac_clientid,
  "productId": 41761,
  "connected": 1,
  "version": "v0.1",
  "services": {
    "ac1": "charger"
  }
}
ac_unregister = copy.deepcopy(ac_registration)
ac_unregister["connected"] = 0
ac_data = {
    "State": 3,
    "Ac/In/L1/I": 1,
    "Ac/In/L1/P": 30,
    "Ac/In/CurrentLimit": 15,
    "Dc/1/Voltage": 14.22,
    "Dc/1/Current" : 5.5,
    "Dc/1/Temperature": 24,
    "Dc/2/Voltage": 12.72,
    "Dc/2/Current" : 1.5,
    "Dc/2/Temperature": 22,
    "Mode": 1,
    "ErrorCode": 0
}

def on_connect_ac(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("device/{}/DBus".format(ac_clientid))
    client.publish("device/{}/Status".format(ac_clientid), json.dumps(ac_registration))

def on_message_ac(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    dbus_msg = json.loads(msg.payload)
    portalId = dbus_msg.get("portalId")

    deviceId = dbus_msg.get("deviceInstance").get("ac1") # UPDATE THIS
    if (deviceId is not None):
      for key in ac_data:
          topic = "W/{}/charger/{}/{}".format(portalId, deviceId, key) # UPDATE THIS
          print("{} = {}".format(topic, ac_data.get(key) ) )
          client.publish(topic, json.dumps({ "value": ac_data.get(key) }) )

client_ac = mqtt.Client()
client_ac.on_connect = on_connect_ac
client_ac.on_message = on_message_ac
client_ac.will_set("device/{}/Status".format(ac_clientid), json.dumps(ac_unregister)) # UPDATE THIS
client_ac.connect("venus.local", 1883, 60)
client_ac.loop_forever()

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

