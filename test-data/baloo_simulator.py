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
ac_clientid = "ac001"
ac_registration = {
  "clientId": ac_clientid,
  "productId": 41761,
  "connected": 1,
  "version": "v0.1",
  "services": {
    "ac1": "accharger"
  }
}
ac_unregister = copy.deepcopy(ac_registration)
ac_unregister["connected"] = 0
ac_data = {
    "State": 3,
    "Ac/In/L1/I": "1",
    "Ac/In/L1/P": "30",
    "Dc/0/Voltage": 14.22,
    "Dc/0/Current" : 5.5,
    "Dc/0/Temperature": 24,
    "Dc/0/Voltage": 12.72,
    "Dc/0/Current" : 1.5,
    "Dc/0/Temperature": 22,
    "Mode": 1
}

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("device/{}/DBus".format(solar_clientid))
    client.publish("device/{}/Status".format(solar_clientid), json.dumps(solar_registration))

# The callback for when a PUBLISH message is received from the server.
def on_message(solar_client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

    dbus_msg = json.loads(msg.payload)
    portalId = dbus_msg.get("portalId")
    deviceId = dbus_msg.get("deviceInstance").get("ss1") # UPDATE THIS
    for key in solar_data:
        topic = "W/{}/solarcharger/{}/{}".format(portalId, deviceId, key) # UPDATE THIS
        print("{} = {}".format(topic, solar_data.get(key) ) )
        client.publish(topic, json.dumps({ "value": solar_data.get(key) }) )

    dbus_msg = json.loads(msg.payload)
    portalId = dbus_msg.get("portalId")
    deviceId = dbus_msg.get("deviceInstance").get("ac1") # UPDATE THIS
    for key in ac_data:
        topic = "W/{}/accharger/{}/{}".format(portalId, deviceId, key) # UPDATE THIS
        print("{} = {}".format(topic, ac_data.get(key) ) )
        client.publish(topic, json.dumps({ "value": ac_data.get(key) }) )

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.will_set("device/{}/Status".format(solar_clientid), json.dumps(solar_unregister)) # UPDATE THIS

client.connect("venus.local", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()

