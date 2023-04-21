import appdaemon.plugins.hass.hassapi as hass
import requests
import json
from urllib.parse import quote


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
            outsideTemp = {
                "state": plantData["outsideTemp"],
                "attributes": {
                    "unit_of_measurement": "°C",
                    "device_class": "temperature",
                },
                "friendly_name": "Elco Outside Temperature",
            }
            _post_data("sensor.elco_outside_temperature", outsideTemp)

        def _post_zoneData(zoneData):
            pass

        try:
            if self.args["ha_url"]:
                # get HA's url from app's first, if configured/overridden by user
                self.log("Using ha_url from app's configuration")
                ha_url = self.args["ha_url"]
            else:
                ha_url = self.config["plugins"]["HASS"]["ha_url"]
        except Exception as e:
            self.log(
                "No Home Assistant URL could be found. Please configure ha_url in the app's configuration. Aborting."
            )
            self.log(e)
            return

        _post_plantData(data["plantData"])
        _post_zoneData(data["zoneData"])

    def get_remocon_data(self, kwargs):
        self.log("Fetching remocon data...")
        try:
            base_url = self.args.get("base_url")
            gateway = self.args.get("gateway_id")
            username = quote(self.args.get("username"), safe="")
            password = quote(self.args.get("password"), safe="")
        except Exception as config_e:
            self.log("There was a problem getting configuration values. Aborting.")
            return
        try:
            login_url = f"{base_url}/R2/Account/Login?returnUrl=HTTP/2"
            payload = f"Email={username}&Password={password}&RememberMe=false"
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Cookie": "browserUtcOffset=-120",
            }
            session = requests.session()
            # login,get session cookie and address for json data
            response = session.post(url=login_url, headers=headers, data=payload)
            result_json = json.loads(response.text)
            if result_json["ok"]:
                # get zone 1 data
                payload = {
                    "useCache": True,
                    "zone": 1,
                    "filter": {"progIds": "null", "plant": True, "zone": True},
                }
                data_url = f"{base_url}/R2/PlantHomeBsb/GetData/{gateway}"
                response = session.post(url=data_url, json=payload)
                if response.status_code == 200:
                    result_json = json.loads(response.text)
                    self.post_to_entities(result_json["data"])
                else:
                    self.error(response.text)
            else:
                self.error(result_json["message"])
            self.log("Done fetching remocon data.")
        except Exception as e:
            self.error(e)
        finally:
            pass
