# elco-remocon-net-appdaemon

[![hacs_badge](https://img.shields.io/badge/HACS-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release][releases-shield]][releases]
[![License][license-shield]](LICENSE.md)
[![Github Actions][github-actions-shield]][github-actions]
![Project Maintenance][maintenance-shield]
[![GitHub Activity][commits-shield]][commits]

ELCO Remocon.net AppDaemon app to fetch data from the gas boiler system via the Elco Remocon-Net cloud service and push them to home-assistant entities.

[![Sponsor Nechry via GitHub Sponsors][github-sponsors-shield]][github-sponsors]

## Installation

### Installing AppDaemon

The backend application for HomeAssistant is written in a python for AppDaemon. This means it requires a working and running installation of AppDaemon.

![hass-add-on-store][hass-add-on-store]

The easiest way to install it is through Home Assistant's Supervisor Add-on Store, it will be automatically connected to your Home Assistant Instance.

### (Optional) Installing Studio Code Server

You will need a way to edit the `apps.yaml` config file in the Appdaemon folder.

Install `Studio Code Server` from Home Assistant's Supervisor Add-on Store to easily edit configuration Files on your HomeAssistant Instance.

Any other method to modify your configuration files will also work.

### Installing HomeAssistant Community Store

`HACS` is the Home Assistant Community Store and allows for community integrations and automation to be updated easily from the Home Assistant web user interface. You will be notified of updates, and they can be installed by a click on a button.

### Installing AppDaemon Backend Application

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=nechry&repository=elco-remocon-net-appdaemon&category=appdaemon)

## Configuration

Create a [Long Lived Access Tokens](https://www.home-assistant.io/docs/authentication/#your-account-profile) for appdaemon, and save it in your `/config/secrets.yaml` file.

Assing the token to the plugins HASS section in `/config/appdaemon/appdaemon.yaml` file.

```yaml
plugins:
    HASS:
      type: hass
      ha_url: http://homeassistant.local:8123
      token: !secret appdaemon_token
```

Ensure to set a valid `ha_url` to match your setup.

### AppDaemon's python packages pre-requisites

No additional python packages are required.

### HACS configuration

To to get `ELCO Remocon.net AppDaemon` work with HACS, you will need to make sure that you enabled AppDaemon automation in HACS, as these are not enabled by default:

- Click on Configuration on the left menu bar in Home Assistant Web UI
- Select Devices & Services
- Select Integrations
- Find HACS and click on Configure
- In the window that opens, make sure that Enable AppDaemon apps discovery & tracking is checked, or check it and click Submit

[AppDaemon discovery and tracking](https://hacs.xyz/docs/categories/appdaemon_apps) enabled for HACS.

### Remocon-Net configuration

It is required to have a working Elco Remocon-Net installation with a gateway. Base on that you have to find your `gateway_id`.

The `gateway_id` is the number you see in the URL when you are logged in to the Elco Remocon-Net cloud service, which you would find at https://www.remocon-net.remotethermo.com

![gateway_id][gateway_id]

### secrets.yaml

Add the following information in your secrets.yaml file according to your Remocon-Net profile:

```yaml
remocon_username: <YOUR_EMAIL>
remocon_password: <YOUR_PASSWORD>
remocon_gateway_id: <YOUR_INSTALLATION_NUMBER>
remocon_bearer_token: <REMOCON_LONG_LIVE_TOKEN>
```

The `remocon_bearer_token` refers to a second long-lived Home Assistant token. Create a new one in your Home Assistant profile page for Remocon app.

Attention: For Apps in the AppDaemon, the `secrets.yaml` file location is define/configurable in `/config/appdaemon/appdaemon.yaml` file.
```yaml
secrets: /config/secrets.yaml
```

In this case I share same  `secrets.yaml` file of Home-Assistant instance.

### apps.yaml

Define your app like the following:

<!-- MARKDOWN-AUTO-DOCS:START (CODE:src=./.apps.example.yaml) -->
<!-- The below code snippet is automatically added from ./.apps.example.yaml -->
```yaml
remocon:
  module: elco-remocon-net-appdaemon
  class: Remocon
  plugin: HASS
  base_url: https://www.remocon-net.remotethermo.com
  username: !secret remocon_username
  password: !secret remocon_password
  gateway_id: !secret remocon_gateway_id
  bearer_token: !secret remocon_bearer_token
  # refresh_rate: 60 # optional
  #ha_url:  # optional, in case hassplugin ha_url undefined
```
<!-- MARKDOWN-AUTO-DOCS:END -->

key | optional | type | default | description
-- | -- | -- | -- | --
`base_url` | False | string | <https://www.remocon-net.remotethermo.com> | Remocon-net cloud service url
`username` | False | string | | Your ELCO username to access remocon-net cloud service, recommended to use secrets.
`password` | False | string | |Your ELCO password to access remocon-net cloud service, recommended to use secrets.
`gateway_id` | False | string | | Your gateway id
`bearer_token` | False | string | | Long-lived Home Assistant token
`refresh_rate` | True | int | 60 | The crawl rate in minutes
`ha_url` | True | string | | HA url for callback

## Usage

- `ELCO Remocon.net AppDaemon` will initiate a login session on Elco Remocon-Net cloud service base on your provided credential.
- On success the AppDaemon will fetch all information of the specified installation provided by the gateway_id
- Last but not least the AppDaemon will push the data to the specified Home Assistant entities.

## Entities

| sensor | Description | source | Detail |
|--- |---|---|---|
| sensor.elco_outside_temperature | Elco Outside Temperature | plantData.outsideTemp | unit_of_measurement: °C  |
| sensor.elco_domestic_hot_water_storage_temperature | Elco Domestic Hot Water Storage Temperature | plantData.dhwStorageTemp | unit_of_measurement: °C |
| sensor.elco_domestic_hot_water_temperature | Elco Domestic Hot Water Temperature | plantData.dhwComfortTemp.value | unit_of_measurement: °C |
| sensor.elco_comfort_room_temperature_setpoint | Elco Comfort room Temperature setpoint | zoneData.chComfortTemp.value | unit_of_measurement: °C |
| sensor.elco_reduced_room_temperature_setpoint | Elco Reduced room Temperature setpoint | zoneData.chReducedTemp.value | unit_of_measurement: °C |
| sensor.elco_room_temperature | Elco Room Temperature | zoneData.roomTemp | unit_of_measurement: °C |
| sensor.elco_desired_room_temperature | Elco Desired Room Temperature | zoneData.desiredRoomTemp | unit_of_measurement: °C |
| sensor.elco_room_operation_mode_heating | Elco Room Operation mode heating | zoneData.mode.value | Protection, Automatic, Reduction, Comfort |
| sensor.elco_cool_comfort_room_temperature_setpoint | Elco Cool Comfort room Temperature setpoint | zoneData.coolComfortTemp.value | |
| sensor.elco_cool_reduced_room_temperature_setpoint | Elco Cool Reduced room Temperature setpoint | zoneData.coolReducedTemp.value | |
| binary_sensor.elco_domestic_hot_water_storage_mode | Elco Domestic Hot Water Storage Mode | plantData.dhwMode.value |  |
| binary_sensor.elco_domestic_hot_water_storage_temperature_error | Elco Domestic Hot Water Storage Temperature Error | plantData.dhwStorageTempError |  |
| binary_sensor.elco_outside_temperature_error | Elco Outside Temperature Error | plantData.outsideTempError |  |
| binary_sensor.elco_heatpump_on | Elco HeatPump On | plantData.heatPumpOn |  |
| binary_sensor.elco_domestic_hot_water_enabled | Elco Domestic Hot Water Enabled | plantData.dhwEnabled |  |
| binary_sensor.elco_has_outside_temperature_probe | Elco has Outside Temperature Probe | plantData.hasOutsideTempProbe |  |
| binary_sensor.elco_flame_sensor | Elco Flame sensor | plantData.flameSensor |  |
| binary_sensor.elco_has_domestic_hot_water_storage_probe | Elco has Domestic Hot Water Storage Probe | plantData.hasDhwStorageProbe |  |
| binary_sensor.elco_room_heating_is_active | Elco Room Heating is Active | zoneData.isHeatingActive |  |
| binary_sensor.elco_room_heating_is_request | Elco Room Heating or Cool is Request | zoneData.heatOrCoolRequest |  |
| binary_sensor.elco_room_cooling_is_active | Elco Room Cooling is Active | zoneData.isCoolingActive |  |
| binary_sensor.elco_room_temperature_error | Elco Room Temperature Error | zoneData.roomTempError |  |

## Limitations

- This appdaemon's app only supports 1 gateway.
- Readonly access, not set point, for the moment.
- No support for Hot Water Heat Pumps

### Tested system

- THISION S boiler
- Altron B boiler
  
###


## License

[MIT](LICENSE)

[hass-add-on-store]: https://github.com/nechry/elco-remocon-net-appdaemon/raw/main/assets/hass-add-on-store.png
[gateway_id]: https://github.com/nechry/elco-remocon-net-appdaemon/raw/main/assets/gateway_id.png

[commits-shield]: https://img.shields.io/github/commit-activity/y/nechry/elco-remocon-net-appdaemon.svg
[commits]: https://github.com/nechry/elco-remocon-net-appdaemon/commits/main
[releases-shield]: https://img.shields.io/github/release/nechry/elco-remocon-net-appdaemon.svg
[releases]: https://github.com/nechry/elco-remocon-net-appdaemon/releases
[license-shield]: https://img.shields.io/github/license/nechry/elco-remocon-net-appdaemon.svg
[maintenance-shield]: https://img.shields.io/maintenance/yes/2023.svg
[github-actions-shield]: https://github.com/nechry/elco-remocon-net-appdaemon/actions/workflows/hacs-validation.yaml/badge.svg
[github-actions]: https://github.com/nechry/elco-remocon-net-appdaemon/actions
[github-sponsors-shield]: https://github.com/nechry/nechry/raw/master/assets/GitHub_Sponsorship_button.png
[github-sponsors]: https://github.com/sponsors/nechry
