import logging
import os
import sys
import json
import dbus

AppDir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1, os.path.join(AppDir, 'ext', 'velib-python'))

from vedbus import VeDbusService
from settingsdevice import SettingsDevice

class MQTTDevice(object):

    def __init__(self, device_status=None, dbus_address=None, debug=False):
        self._dbus_address = dbus_address
        self._dbus_conn = (dbus.SessionBus() if 'DBUS_SESSION_BUS_ADDRESS' in os.environ else dbus.SystemBus()) \
			if dbus_address is None \
			else dbus.bus.BusConnection(dbus_address)
        self._status = device_status
        self._clientId = device_status["clientId"]
        self._settings = SettingsDevice(bus=self._dbus_conn, supportedSettings={}, eventCallback=self._handle_changed_setting)
        self._services = {}
        self._register_device_services()

    def _handle_changed_setting(setting, oldvalue, newvalue):
        print("setting changed, setting: {}, old: {}, new: {}".format(setting, oldvalue, newvalue))

    def _serviceId(self, service):
        return 'mqtt_{}_{}'.format(self._clientId, service)
    

    def _register_device_services(self):
        for service in self._status["services"]:
            path = "/Settings/Devices/{}/ClassAndVrmInstance".format(self._serviceId(service)), "{}:1".format(service)
            res = self._settings.addSetting(path, None, None)
            s, device_instance = res.get_value().split(':')
            logging.info("Registered Service under %s (%s)", res.get_value(), device_instance)
            self._services[service] = device_instance

    def device_instance(self):
        return self._services
