# nws_alerts_array


[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]

_Alerts from the US National Weather Service_

## Installation

### Installation via HACS

Unless you have a good reason not to, you probably want to install this component via HACS(Home Assistant Community Store)
1. Ensure that [HACS](https://hacs.xyz/) is installed.
1. Navigate to HACS -> Integrations
1. Open the three-dot menu and select 'Custom Repositories'
1. Put 'https://github.com/Snuffy2/nws_alerts_array' into the 'Repository' textbox.
1. Select 'Integration' as the category
1. Press 'Add'.
1. Find the NWS Alerts Array integration in the HACS integration list and install it
1. Add your configuration
1. Restart Home Assistant.

### Manual Installation

You probably do not want to do this! Use the HACS method above unless you have a very good reason why you are installing manually

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `nws_alerts_array`.
1. Download _all_ the files from the `custom_components/nws_alerts_array/` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Add your configuration
1. Restart Home Assistant

## Configuration

<b>Manually via an entry in your configuration.yaml file:</b>

To create a sensor instance add the following configuration to your sensor definitions using the zone_id found above:

```
- platform: nws_alerts_array
  zone_id: 'PAC049'
```

or enter comma separated values for multiple zones:

```
- platform: nws_alerts_array
  zone_id: 'PAC049,WVC031'
```

After you restart Home Assistant then you should have a new sensor called "sensor.nws_alerts_array" in your system.

You can overide the sensor default name ("sensor.nws_alerts_array") to one of your choosing by setting the "name:" option:

```
- platform: nws_alerts_array
  zone_id: 'INZ009,INC033'
  name: My NWS Alerts Sensor
```

Using the configuration example above the sensor will then be called "sensor.my_nws_alerts_sensor"


## Notes:

* An updated version of the nws_alerts integration with the results in arrays for easier splitting of the alerts
* This integration retrieves updated weather alerts every minute from the US NWS API.
* The integration presents the number of currently active alerts as the state of the sensor and lists many alert details as a list in the attributes of the sensor.
* The sensor that is created is used in my "NWS Alerts Custom" package - https://github.com/Snuffy2/nws_alerts_array/blob/main/packages/nws_alerts_custom_package.yaml
* To enable detailed logging for this component, add the following to your configuration.yaml file
```yaml
  logger:
    default: warn
    logs:
      custom_components.nws_alerts_array: debug 
```


## Based on work from:

* Original Integration by [@eracknaphobia](https://github.com/eracknaphobia): [nws_custom_component](https://github.com/eracknaphobia/nws_custom_component)
* Subsequent Integration by [@finity69x2](https://github.com/finity69x2): [nws_alerts](https://github.com/finity69x2/nws_alerts)

## Contributions are welcome!

***

[nws_alerts_array]: https://github.com/Snuffy2/nws_alerts_array
[commits-shield]: https://img.shields.io/github/commit-activity/y/Snuffy2/nws_alerts_array?style=for-the-badge
[commits]: https://github.com/Snuffy2/nws_alerts_array/commits
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/Snuffy2/nws_alerts_array.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/v/release/Snuffy2/nws_alerts_array?style=for-the-badge
[releases]: https://github.com/Snuffy2/nws_alerts_array/releases
