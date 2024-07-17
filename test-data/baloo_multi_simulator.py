import paho.mqtt.client as mqtt
import json
import copy

multi_clientid = "ml001"
multi_registration = {
  "clientId": multi_clientid,
  "productId": 9824,
  "connected": 1,
  "version": "v0.1",
  "services": {
    "ml1": "multi"
  }
}
multi_unregister = copy.deepcopy(multi_registration)
multi_unregister["connected"] = 0
multi_data = {
    "State": 3,
    "Ac/In/1/L1/V": 230,
    "Ac/In/1/L1/F": 60,
    "Ac/In/1/L1/I": 1,
    "Ac/In/1/L1/P": 30,
    "Dc/1/Voltage": 14.22,
    "Dc/1/Current" : 5.5,
    "Dc/1/Temperature": 24,
    "Dc/2/Voltage": 12.72,
    "Dc/2/Current" : 1.5,
    "Dc/2/Temperature": 22,
    "Mode": 1,
    "ErrorCode": 0
}

def on_connect_multi(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("device/{}/DBus".format(multi_clientid))
    client.publish("device/{}/Status".format(multi_clientid), json.dumps(multi_registration))

def on_message_multi(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    dbus_msg = json.loads(msg.payload)
    portalId = dbus_msg.get("portalId")

    deviceId = dbus_msg.get("deviceInstance").get("ml1") # UPDATE THIS
    if (deviceId is not None):
      for key in multi_data:
          topic = "W/{}/charger/{}/{}".format(portalId, deviceId, key) # UPDATE THIS
          print("{} = {}".format(topic, multi_data.get(key) ) )
          client.publish(topic, json.dumps({ "value": multi_data.get(key) }) )

client_multi = mqtt.Client()
client_multi.on_connect = on_connect_multi
client_multi.on_message = on_message_multi
client_multi.will_set("device/{}/Status".format(multi_clientid), json.dumps(multi_unregister)) # UPDATE THIS
client_multi.connect("venus.local", 1883, 60)
client_multi.loop_forever()

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

