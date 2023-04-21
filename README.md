# elco-remocon-net-appdaemon

ELCO Remocon.net AppDaemon app to fetch data from the gas boiler system via the Elco Remocon-Net cloud service and push them to home-assistant entities.

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

## Installation

### Installing AppDaemon

The backend application for HomeAssistant is written in a python for AppDaemon. This means it requires a working and running installation of AppDaemon.

![hass-add-on-store][hass-add-on-store]

The easiest way to install it is through Home Assistant's Supervisor Add-on Store, it will be automatically connected to your Home Assistant Instance.

### Installing Studio Code Server

You will need a way to edit the `apps.yaml` config file in the Appdaemon folder.

Install `Studio Code Server` from Home Assistant's Supervisor Add-on Store to easily edit configuration Files on your HomeAssistant Instance.

### Installing HomeAssistant Community Store

`HACS` is the Home Assistant Community Store and allows for community integrations and automation to be updated easily from the Home Assistant web user interface. You will be notified of updates, and they can be installed by a click on a button.

### Installing AppDaemon Backend Application

- Click on `HACS` on the left menu bar in Home Assistant Web UI
- Select the three dots in the top right corner.
- Select `Custom repositories`
- Add the following URL: `https://github.com/nechry/elco-remocon-net-appdaemon` to the repository.
- Select `AppDaemon` for the category.
- Click the `ADD` button.
- Click on `Automation` in the right panel
- Click on Explore & download repositories in the bottom right corner
- Search for `ELCO Remocon.net AppDaemon`, and click on `ELCO Remocon.net AppDaemon` in the list that appears
- In the bottom right corner of the panel that appears, click on Download this repository with HACS
- A confirmation panel will appear, click on Download, and wait for HACS to proceed with the download
- The Backend Application is now installed, and HACS will inform you when updates are available

## Configuration

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

### secrets.yaml

Add the following information in your secrets.yaml file according to your Remocon-Net profile:

```yaml
username: <YOUR_EMAIL>
password: <YOUR_PASSWORD>
gateway_id: <YOUR_INSTALLATION_NUMBER>
bearer_token: <HA_LONG_LIVE_TOKEN>
```

The `bearer_token` refers to a long-lived Home Assistant token. You can create one in your Home Assistant profile page.

### apps.yaml

Define your app like the following:

<!-- MARKDOWN-AUTO-DOCS:START (CODE:src=./apps.example.yaml) -->
<!-- The below code snippet is automatically added from ./apps.example.yaml -->
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
| binary_sensor.elco_domestic_hot_water_storage_mode | Elco Domestic Hot Water Storage Mode | plantData.dhwMode.value |  |
| binary_sensor.elco_domestic_hot_water_storage_temperature_error | Elco Domestic Hot Water Storage Temperature Error | plantData.dhwStorageTempError |  |
| binary_sensor.elco_outside_temperature_error | Elco Outside Temperature Error | plantData.outsideTempError |  |
| binary_sensor.elco_heatpump_on | Elco HeatPump On | plantData.heatPumpOn |  |
| binary_sensor.elco_domestic_hot_water_enabled | Elco Domestic Hot Water Enabled | plantData.dhwEnabled |  |
| binary_sensor.elco_room_heating_is_active | Elco Room Heating is Active | zoneData.isHeatingActive |  |
| binary_sensor.elco_room_heating_is_request | Elco Room Heating is Request | zoneData.heatOrCoolRequest |  |

## Limitations

This appdaemon's app only supports 1 gateway.
Readonly access, not set point, for the moment.

## License

[MIT](LICENSE)

[hass-add-on-store]: assets/hass-add-on-store.png
