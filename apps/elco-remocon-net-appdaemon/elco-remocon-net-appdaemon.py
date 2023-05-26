import hassapi as hass
import requests
import json
from urllib.parse import quote, urljoin
import posixpath


class Remocon(hass.Hass):
    def initialize(self):
        refresh_rate = self.args.get("refresh_rate")
        if refresh_rate is None:
            refresh_rate = 60
        self.log(f"Will fetch remocon.net data every {refresh_rate} min")
        self.run_every(self.get_remocon_data, "now", refresh_rate * 60)

    def post_to_entities(self, data):
        self.log("Posting to entities...")

        def _post_data(sensor, payload):
            entity_url = f"{ha_url}/api/states/{sensor}"
            token = "Bearer {}".format(self.args["bearer_token"])
            headers = {"Authorization": token, "Content-Type": "application/json"}
            try:
                result = requests.post(entity_url, json=payload, headers=headers)
                self.log(f"POST'ed {sensor} to {entity_url}")
            except Exception as e:
                self.log(e)

        def _post_plantData(plantData):
            elco_outside_temperature = {
                "unique_id": "elco_outside_temperature",
                "state": plantData["outsideTemp"],
                "attributes": {
                    "unit_of_measurement": "°C",
                    "device_class": "temperature",
                },
                "friendly_name": "Elco Outside Temperature",
            }
            _post_data("sensor.elco_outside_temperature", elco_outside_temperature)

            elco_domestic_hot_water_storage_temperature = {
                "unique_id": "elco_domestic_hot_water_storage_temperature",
                "state": plantData["dhwStorageTemp"],
                "attributes": {
                    "unit_of_measurement": "°C",
                    "device_class": "temperature",
                },
                "friendly_name": "Elco Domestic Hot Water Storage Temperature",
            }
            _post_data(
                "sensor.elco_domestic_hot_water_storage_temperature",
                elco_domestic_hot_water_storage_temperature,
            )

            elco_domestic_hot_water_temperature = {
                "unique_id": "elco_domestic_hot_water_temperature",
                "state": plantData["dhwComfortTemp"]["value"],
                "attributes": {
                    "unit_of_measurement": "°C",
                    "device_class": "temperature",
                    "min": plantData["dhwComfortTemp"]["min"],
                    "max": plantData["dhwComfortTemp"]["max"],
                    "step": plantData["dhwComfortTemp"]["step"],
                },
                "friendly_name": "Elco Domestic Hot Water Storage Temperature",
            }
            _post_data(
                "sensor.elco_domestic_hot_water_temperature",
                elco_domestic_hot_water_temperature,
            )

            elco_domestic_hot_water_reduced_temperature = {
                "unique_id": "elco_domestic_hot_water_reduced_temperature",
                "state": plantData["dhwReducedTemp"]["value"],
                "attributes": {
                    "unit_of_measurement": "°C",
                    "device_class": "temperature",
                    "min": plantData["dhwReducedTemp"]["min"],
                    "max": plantData["dhwReducedTemp"]["max"],
                    "step": plantData["dhwReducedTemp"]["step"],
                },
                "friendly_name": "Elco Domestic Hot Water Storage Reduced Temperature",
            }
            _post_data(
                "sensor.elco_domestic_hot_water_reduced_temperature",
                elco_domestic_hot_water_reduced_temperature,
            )

            elco_domestic_hot_water_storage_mode = {
                "unique_id": "elco_domestic_hot_water_storage_mode",
                "state": "on" if plantData["dhwMode"]["value"] == 1 else "off",
                "attributes": {
                    "device_class": "running",
                },
                "icon": "mdi:hvac",
                "friendly_name": "Elco Domestic Hot Water Storage Mode",
            }
            _post_data(
                "binary_sensor.elco_domestic_hot_water_storage_mode",
                elco_domestic_hot_water_storage_mode,
            )

            elco_domestic_hot_water_storage_temperature_error = {
                "unique_id": "elco_domestic_hot_water_storage_temperature_error",
                "state": "on" if plantData["dhwStorageTempError"] == 1 else "off",
                "attributes": {
                    "device_class": "problem",
                },
                "icon": "mdi:radiator",
                "friendly_name": "Elco Domestic Hot Water Storage Temperature Error",
            }
            _post_data(
                "binary_sensor.elco_domestic_hot_water_storage_temperature_error",
                elco_domestic_hot_water_storage_temperature_error,
            )

            elco_outside_temperature_error = {
                "unique_id": "elco_outside_temperature_error",
                "state": "on" if plantData["outsideTempError"] == 1 else "off",
                "attributes": {
                    "device_class": "problem",
                },
                "icon": "mdi:radiator",
                "friendly_name": "Elco Outside Temperature Error",
            }
            _post_data(
                "binary_sensor.elco_outside_temperature_error",
                elco_outside_temperature_error,
            )

            elco_heatpump_on = {
                "unique_id": "elco_heatpump_on",
                "state": "on" if plantData["heatPumpOn"] == 1 else "off",
                "attributes": {
                    "device_class": "running",
                },
                "icon": "mdi:radiator",
                "friendly_name": "Elco HeatPump On",
            }
            _post_data("binary_sensor.elco_heatpump_on", elco_heatpump_on)

            elco_domestic_hot_water_enabled = {
                "unique_id": "elco_domestic_hot_water_enabled",
                "state": "on" if plantData["dhwEnabled"] == 1 else "off",
                "attributes": {
                    "device_class": "running",
                },
                "icon": "mdi:radiator",
                "friendly_name": "Elco Domestic Hot Water Enabled",
            }
            _post_data(
                "binary_sensor.elco_domestic_hot_water_enabled",
                elco_domestic_hot_water_enabled,
            )

        def _post_zoneData(zoneData):
            elco_comfort_room_temperature_setpoint = {
                "unique_id": "elco_comfort_room_temperature_setpoint",
                "state": zoneData["chComfortTemp"]["value"],
                "attributes": {
                    "unit_of_measurement": "°C",
                    "device_class": "temperature",
                    "min": zoneData["chComfortTemp"]["min"],
                    "max": zoneData["chComfortTemp"]["max"],
                    "step": zoneData["chComfortTemp"]["step"],
                },
                "friendly_name": "Elco Comfort room Temperature setpoint",
            }
            _post_data(
                "sensor.elco_comfort_room_temperature_setpoint",
                elco_comfort_room_temperature_setpoint,
            )

            elco_reduced_room_temperature_setpoint = {
                "unique_id": "elco_reduced_room_temperature_setpoint",
                "state": zoneData["chReducedTemp"]["value"],
                "attributes": {
                    "unit_of_measurement": "°C",
                    "device_class": "temperature",
                    "min": zoneData["chReducedTemp"]["min"],
                    "max": zoneData["chReducedTemp"]["max"],
                    "step": zoneData["chReducedTemp"]["step"],
                },
                "friendly_name": "Elco Reduced room Temperature setpoint",
            }
            _post_data(
                "sensor.elco_reduced_room_temperature_setpoint",
                elco_reduced_room_temperature_setpoint,
            )

            elco_room_temperature = {
                "unique_id": "elco_room_temperature",
                "state": zoneData["roomTemp"],
                "attributes": {
                    "unit_of_measurement": "°C",
                    "device_class": "temperature",
                },
                "friendly_name": "Elco Room Temperature",
            }
            _post_data("sensor.elco_room_temperature", elco_room_temperature)

            elco_desired_room_temperature = {
                "unique_id": "elco_desired_room_temperature",
                "state": zoneData["desiredRoomTemp"],
                "attributes": {
                    "unit_of_measurement": "°C",
                    "device_class": "temperature",
                },
                "friendly_name": "Elco Desired Room Temperature",
            }
            _post_data(
                "sensor.elco_desired_room_temperature", elco_desired_room_temperature
            )

            mode_dict = {0: "Off", 1: "Comfort", 2: "Reduced", 3: "Frost Protection"}
            elco_room_operation_mode_heating = {
                "unique_id": "elco_room_operation_mode_heating",
                "state": mode_dict.get(zoneData["mode"]["value"]),
                "attributes": {},
                "icon": "mdi:radiator",
                "friendly_name": "Elco Room Operation mode heating",
            }
            _post_data(
                "sensor.elco_room_operation_mode_heating",
                elco_room_operation_mode_heating,
            )

            elco_room_heating_is_active = {
                "unique_id": "elco_room_heating_is_active",
                "state": "on" if zoneData["isHeatingActive"] == 1 else "off",
                "attributes": {
                    "device_class": "running",
                },
                "friendly_name": "Elco Room Heating is Active",
            }
            _post_data(
                "binary_sensor.elco_room_heating_is_active", elco_room_heating_is_active
            )

            elco_room_heating_is_request = {
                "unique_id": "elco_room_heating_is_request",
                "state": "on" if zoneData["heatOrCoolRequest"] == 1 else "off",
                "attributes": {
                    "device_class": "problem",
                },
                "friendly_name": "Elco Room Heating is Request",
            }
            _post_data(
                "binary_sensor.elco_room_heating_is_request",
                elco_room_heating_is_request,
            )

        try:
            if self.args["ha_url"]:
                # get HA's url from app's first, if configured/overridden by user
                self.log("Using ha_url from app's configuration")
                ha_url = self.args["ha_url"]
            else:
                ha_url = self.config["plugins"]["HASS"]["ha_url"]
        except Exception as e:
            self.error(
                "No Home Assistant URL could be found. Please configure ha_url in the app's configuration. Aborting."
            )
            self.error(e)
            return

        _post_plantData(data["plantData"])
        _post_zoneData(data["zoneData"])

    def get_remocon_data(self, kwargs):
        self.log("Fetching remocon data...")
        try:
            base_url = self.args.get("base_url")
            if base_url is None:
                base_url = "https://www.remocon-net.remotethermo.com"
            zone = self.args.get("zone")
            if zone is None:
                zone = 1
            gateway = self.args.get("gateway_id")
            if not gateway:
                self.error(
                    "There was a problem getting configuration values, gateway_id is not defined. Aborting."
                )
                return
            username = quote(self.args.get("username"), safe="")
            password = quote(self.args.get("password"), safe="")
        except Exception:
            self.error("There was a problem getting configuration values. Aborting.")
            return
        try:
            login_url = urljoin(base_url, "R2/Account/Login?returnUrl=HTTP/2")
            payload = f"Email={username}&Password={password}&RememberMe=false"
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Cookie": "browserUtcOffset=-120",
            }
            session = requests.session()
            # login, get session cookie and address for json data
            response = session.post(url=login_url, headers=headers, data=payload)
            if response.status_code == 200:
                result_json = json.loads(response.text)
                if result_json["ok"]:
                    # get zone data
                    payload = {
                        "useCache": True,
                        "zone": zone,
                        "filter": {"progIds": "null", "plant": True, "zone": True},
                    }
                    data_url = urljoin(
                        base_url, posixpath.join("R2/PlantHomeBsb/GetData", gateway)
                    )
                    response = session.post(url=data_url, json=payload)
                    if response.status_code == 200:
                        result_json = json.loads(response.text)
                        self.post_to_entities(result_json["data"])
                        self.log("Done fetching remocon data.")
                    else:
                        error_message = response.text
                        self.error(f"Fetching error: {error_message}")
                else:
                    error_message = result_json["message"]
                    self.error(f"Authentication failed: {error_message}")
            else:
                error_message = response.text
                self.error(f"Authentication error: {error_message}")
        except Exception as e:
            self.error(f"Unhandled exception: {e}")
