import hassapi as hass
from datetime import datetime
import requests
import json
from urllib.parse import quote, urljoin
import posixpath

# Weekday index -> entity-id suffix. The Remocon NET front-end uses JavaScript's
# Date.getDay() for the `days` field on schedule slices, so 0 is Sunday.
WEEKDAY_SUFFIX = {
    0: "sunday",
    1: "monday",
    2: "tuesday",
    3: "wednesday",
    4: "thursday",
    5: "friday",
    6: "saturday",
}


class Remocon(hass.Hass):
    def initialize(self):
        refresh_rate = self.args.get("refresh_rate")
        if refresh_rate is None:
            refresh_rate = 60
        self.log(f"Will fetch remocon.net data every {refresh_rate} min")
        self.run_every(self.get_remocon_data, datetime.now(), refresh_rate * 60)
        # fetch data immediately on startup
        self.log("Fetching remocon.net data immediately on startup")        
        self.get_remocon_data(None)
        self.log("Fetching remocon.net data completed")

    def post_to_entities(self, data):
        self.log("Posting to entities...")

        def _post_data(sensor, payload):
            try:
                # elco_sensor = self.get_entity(sensor)
                # if elco_sensor is None:
                entity_url = f"{ha_url}/api/states/{sensor}"
                token = "Bearer {}".format(self.args["bearer_token"])
                headers = {"Authorization": token, "Content-Type": "application/json"}
                requests.post(entity_url, json=payload, headers=headers)
                self.log(f"Set state on entity {sensor}")
                # else:
                #     elco_sensor.set_state(state = payload["state"], attributes = payload["attributes"])
                #     self.log(f"update state of {sensor}")

            except Exception as e:
                self.log(e)

        def _post_plantData(plantData):
            data = {
                "state": plantData["outsideTemp"],
                "attributes": {
                    "unit_of_measurement": "°C",
                    "device_class": "temperature",
                    "friendly_name": "Elco Outside Temperature",
                },
            }
            _post_data("sensor.elco_outside_temperature", data)

            data = {
                "state": plantData["dhwStorageTemp"],
                "attributes": {
                    "unit_of_measurement": "°C",
                    "device_class": "temperature",
                    "friendly_name": "Elco Domestic Hot Water Storage Temperature",
                },
            }
            _post_data(
                "sensor.elco_domestic_hot_water_storage_temperature",
                data,
            )

            elco_domestic_hot_water_temperature = {
                "state": plantData["dhwComfortTemp"]["value"],
                "attributes": {
                    "unit_of_measurement": "°C",
                    "device_class": "temperature",
                    "min": plantData["dhwComfortTemp"]["min"],
                    "max": plantData["dhwComfortTemp"]["max"],
                    "step": plantData["dhwComfortTemp"]["step"],
                    "friendly_name": "Elco Domestic Hot Water Storage Temperature",
                },
            }
            _post_data(
                "sensor.elco_domestic_hot_water_temperature",
                elco_domestic_hot_water_temperature,
            )

            data = {
                "state": plantData["dhwReducedTemp"]["value"],
                "attributes": {
                    "unit_of_measurement": "°C",
                    "device_class": "temperature",
                    "min": plantData["dhwReducedTemp"]["min"],
                    "max": plantData["dhwReducedTemp"]["max"],
                    "step": plantData["dhwReducedTemp"]["step"],
                    "friendly_name": "Elco Domestic Hot Water Storage Reduced Temperature",
                },
            }
            _post_data(
                "sensor.elco_domestic_hot_water_reduced_temperature",
                data,
            )

            data = {
                "state": "on" if plantData["dhwMode"]["value"] == 1 else "off",
                "attributes": {
                    "device_class": "running",
                    "friendly_name": "Elco Domestic Hot Water Storage Mode",
                    "icon": "mdi:hvac",
                },
            }
            _post_data(
                "binary_sensor.elco_domestic_hot_water_storage_mode",
                data,
            )

            data = {
                "state": "on" if plantData["dhwStorageTempError"] == 1 else "off",
                "attributes": {
                    "device_class": "problem",
                    "icon": "mdi:radiator",
                    "friendly_name": "Elco Domestic Hot Water Storage Temperature Error",
                },
            }
            _post_data(
                "binary_sensor.elco_domestic_hot_water_storage_temperature_error",
                data,
            )

            data = {
                "state": "on" if plantData["outsideTempError"] == 1 else "off",
                "attributes": {
                    "device_class": "problem",
                    "icon": "mdi:radiator",
                    "friendly_name": "Elco Outside Temperature Error",
                },
            }
            _post_data(
                "binary_sensor.elco_outside_temperature_error",
                data,
            )

            data = {
                "state": "on" if plantData["hasOutsideTempProbe"] == 1 else "off",
                "attributes": {
                    "device_class": "connectivity",
                    "icon": "mdi:thermometer-probe",
                    "friendly_name": "Elco has Outside Temperature Probe",
                },
            }
            _post_data(
                "binary_sensor.elco_has_outside_temperature_probe",
                data,
            )

            data = {
                "state": "on" if plantData["flameSensor"] == 1 else "off",
                "attributes": {
                    "device_class": "connectivity",
                    "icon": "mdi:fire",
                    "friendly_name": "Elco Flame sensor",
                },
            }
            _post_data(
                "binary_sensor.elco_flame_sensor",
                data,
            )

            data = {
                "state": "on" if plantData["hasDhwStorageProbe"] == 1 else "off",
                "attributes": {
                    "device_class": "connectivity",
                    "friendly_name": "Elco has Domestic Hot Water Storage Probe",
                    "icon": "mdi:thermometer-probe",
                },
            }
            _post_data(
                "binary_sensor.elco_has_domestic_hot_water_storage_probe",
                data,
            )

            data = {
                "state": "on" if plantData["heatPumpOn"] == 1 else "off",
                "attributes": {
                    "device_class": "running",
                    "icon": "mdi:radiator",
                    "friendly_name": "Elco HeatPump On",
                },
            }
            _post_data("binary_sensor.elco_heatpump_on", data)

            data = {
                "state": "on" if plantData["dhwEnabled"] == 1 else "off",
                "attributes": {
                    "device_class": "running",
                    "icon": "mdi:radiator",
                    "friendly_name": "Elco Domestic Hot Water Enabled",
                },
            }
            _post_data(
                "binary_sensor.elco_domestic_hot_water_enabled",
                data,
            )

        def _post_zoneData(zoneData):
            data = {
                "state": zoneData["chComfortTemp"]["value"],
                "attributes": {
                    "unit_of_measurement": "°C",
                    "device_class": "temperature",
                    "min": zoneData["chComfortTemp"]["min"],
                    "max": zoneData["chComfortTemp"]["max"],
                    "step": zoneData["chComfortTemp"]["step"],
                    "friendly_name": "Elco Comfort room Temperature setpoint",
                },
            }
            _post_data(
                "sensor.elco_comfort_room_temperature_setpoint",
                data,
            )

            data = {
                "state": zoneData["coolComfortTemp"]["value"],
                "attributes": {
                    "unit_of_measurement": "°C",
                    "device_class": "temperature",
                    "min": zoneData["coolComfortTemp"]["min"],
                    "max": zoneData["coolComfortTemp"]["max"],
                    "step": zoneData["coolComfortTemp"]["step"],
                    "friendly_name": "Elco Cool Comfort room Temperature setpoint",
                },
            }
            _post_data(
                "sensor.elco_cool_comfort_room_temperature_setpoint",
                data,
            )

            data = {
                "state": zoneData["coolReducedTemp"]["value"],
                "attributes": {
                    "unit_of_measurement": "°C",
                    "device_class": "temperature",
                    "min": zoneData["coolReducedTemp"]["min"],
                    "max": zoneData["coolReducedTemp"]["max"],
                    "step": zoneData["coolReducedTemp"]["step"],
                    "friendly_name": "Elco Cool Reduced room Temperature setpoint",
                },
            }
            _post_data(
                "sensor.elco_cool_reduced_room_temperature_setpoint",
                data,
            )

            data = {
                "state": zoneData["chReducedTemp"]["value"],
                "attributes": {
                    "unit_of_measurement": "°C",
                    "device_class": "temperature",
                    "min": zoneData["chReducedTemp"]["min"],
                    "max": zoneData["chReducedTemp"]["max"],
                    "step": zoneData["chReducedTemp"]["step"],
                    "friendly_name": "Elco Reduced room Temperature setpoint",
                },
            }
            _post_data(
                "sensor.elco_reduced_room_temperature_setpoint",
                data,
            )

            data = {
                "state": zoneData["roomTemp"],
                "attributes": {
                    "unit_of_measurement": "°C",
                    "device_class": "temperature",
                    "friendly_name": "Elco Room Temperature",
                },
            }
            _post_data("sensor.elco_room_temperature", data)

            data = {
                "state": zoneData["desiredRoomTemp"],
                "attributes": {
                    "unit_of_measurement": "°C",
                    "device_class": "temperature",
                    "friendly_name": "Elco Desired Room Temperature",
                },
            }
            _post_data("sensor.elco_desired_room_temperature", data)

            mode_dict = {0: "Protection", 1: "Automatic", 2: "Reduced", 3: "Comfort"}
            data = {
                "state": mode_dict.get(zoneData["mode"]["value"]),
                "attributes": {
                    "icon": "mdi:radiator",
                    "friendly_name": "Elco Room Operation mode heating",
                },
            }
            _post_data(
                "sensor.elco_room_operation_mode_heating",
                data,
            )

            data = {
                "state": "on" if zoneData["isHeatingActive"] == 1 else "off",
                "attributes": {
                    "device_class": "running",
                    "friendly_name": "Elco Room Heating is Active",
                },
            }
            _post_data("binary_sensor.elco_room_heating_is_active", data)

            data = {
                "state": "on" if zoneData["isCoolingActive"] == 1 else "off",
                "attributes": {
                    "device_class": "running",
                    "friendly_name": "Elco Room Cooling is Active",
                },
            }
            _post_data("binary_sensor.elco_room_cooling_is_active", data)

            data = {
                "state": "on" if zoneData["heatOrCoolRequest"] == 1 else "off",
                "attributes": {
                    "device_class": "problem",
                    "friendly_name": "Elco Room Heating or Cool is Request",
                },
            }
            _post_data(
                "binary_sensor.elco_room_heating_is_request",
                data,
            )

            data = {
                "state": "on" if zoneData["roomTempError"] == 1 else "off",
                "attributes": {
                    "device_class": "problem",
                    "friendly_name": "Elco Room Temperature Error",
                },
            }
            _post_data(
                "binary_sensor.elco_room_temperature_error",
                data,
            )

        def _post_schedule(weeklyPlan, comfort_temp, reduced_temp):
            """Publish one sensor per weekday carrying that day's slice list.

            State is the number of slices for the day, so HA history stays
            useful; the slices themselves are attributes.

            weeklyPlan shape, from the timeProgs entry of the GetData response:
              {
                plans: [
                  {days: [<int day-of-week>, ...],
                   slices: [{from: <minutes from midnight>, temp: <0|1>}, ...]},
                  ...
                ],
                allowedTemp, defaultTemp, baseTemp, tick, maxSwitches, ext, pilot
              }

            `slice.temp` is a mode flag (0 = reduced, 1 = comfort), NOT a
            temperature in degrees. The actual setpoints are scalars held
            elsewhere, in zoneData.chComfortTemp / chReducedTemp, which is why
            they are passed in here rather than read off the slice.
            """
            plans = (weeklyPlan or {}).get("plans") or []
            by_day = {d: [] for d in WEEKDAY_SUFFIX}
            for plan in plans:
                if not plan:
                    continue
                slices = sorted(
                    [s for s in (plan.get("slices") or []) if s is not None],
                    key=lambda s: s.get("from", 0),
                )
                for d in plan.get("days") or []:
                    if d in by_day:
                        by_day[d] = slices

            def mode_for(flag):
                return "comfort" if flag == 1 else "reduced"

            def temp_for(flag):
                return comfort_temp if flag == 1 else reduced_temp

            for day_idx, suffix in WEEKDAY_SUFFIX.items():
                slices = by_day[day_idx]
                # Two attributes, because a slice list alone is awkward to
                # template against:
                #  - `slices`:    the raw list, plus an HH:MM convenience field
                #  - `intervals`: each slice closed at the next one (or 24:00),
                #                 so a card can render spans directly
                rendered = []
                intervals = []
                for i, s in enumerate(slices):
                    m = int(s.get("from", 0))
                    flag = s.get("temp")
                    rendered.append(
                        {
                            "from_min": m,
                            "from_hhmm": f"{m // 60:02d}:{m % 60:02d}",
                            "flag": flag,
                            "mode": mode_for(flag),
                            "temp": temp_for(flag),
                        }
                    )
                    if (i + 1) < len(slices):
                        end_m = int(slices[i + 1].get("from", 1440))
                    else:
                        end_m = 1440
                    intervals.append(
                        {
                            "start_min": m,
                            "end_min": end_m,
                            "start_hhmm": f"{m // 60:02d}:{m % 60:02d}",
                            "end_hhmm": f"{end_m // 60:02d}:{end_m % 60:02d}",
                            "mode": mode_for(flag),
                            "temp": temp_for(flag),
                        }
                    )
                _post_data(
                    f"sensor.elco_schedule_{suffix}",
                    {
                        "state": len(rendered),
                        "attributes": {
                            "friendly_name": f"Elco Schedule {suffix.capitalize()}",
                            "icon": "mdi:calendar-clock",
                            "unit_of_measurement": "slices",
                            "slices": rendered,
                            "intervals": intervals,
                            "ext": (weeklyPlan or {}).get("ext"),
                            "max_switches": (weeklyPlan or {}).get("maxSwitches"),
                        },
                    },
                )

        try:
            if self.args.get("ha_url"):
                # get HA's url from app's first, if configured/overridden by user
                self.log("Using ha_url from app's configuration")
                ha_url = self.args["ha_url"]
            else:
                self.log("Using ha_url from plugins's HASS configuration")
                ha_url = self.config["plugins"]["HASS"]["ha_url"]
        except Exception as e:
            self.error(
                "No Home Assistant URL could be found. Please configure ha_url in the app's configuration. Aborting."
            )
            self.error(e)
            return

        _post_plantData(data["plantData"])
        _post_zoneData(data["zoneData"])
        # `timeProgs` is only present when the GetData payload asks for it by
        # programme id (see the filter in get_remocon_data). Stay quiet when it
        # is absent so nothing changes for a plant that returns no schedule.
        time_progs = data.get("timeProgs") or []
        if time_progs:
            comfort_c = float(data["zoneData"]["chComfortTemp"]["value"])
            reduced_c = float(data["zoneData"]["chReducedTemp"]["value"])
            weekly_plan = (time_progs[0] or {}).get("weeklyPlan") or {}
            _post_schedule(weekly_plan, comfort_c, reduced_c)

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
                    # progIds selects which time programmes come back in
                    # `data.timeProgs`. Per the BSB enum, 1..6 are heating
                    # zones ChZn1..ChZn6, 7 is DHW and 9..14 are the cooling
                    # zones, so [zone] asks for the schedule of the heating
                    # zone this app is already configured for. The previous
                    # value was the string "null", which requests none.
                    payload = {
                        "useCache": True,
                        "zone": zone,
                        "filter": {"progIds": [zone], "plant": True, "zone": True},
                    }
                    data_url = urljoin(
                        base_url, posixpath.join("R2/PlantHomeBsb/GetData", gateway)
                    )
                    self.log(f"Parameters gatewayId: {gateway} zone: {payload}")
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
