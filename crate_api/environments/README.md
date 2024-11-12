This folder contains Environment YAML files defining labgrid driver and resource configurations for hardware platforms supported by 'crate_api'.
https://labgrid.readthedocs.io/en/latest/configuration.html#environment-configuration

All resources and drivers are defined in the following default way under the 'main' target which is the default. Additional targets may be included for specific configurations or use-cases.

### Main Target Driver Naming Scheme 
Drivers defined in the environment file 'main' target are named according to the following guidelines:

- Names are lower case words seperated by dashes with a trailing decimal integers: `<portname>-<portnumber>`
- Labels and numbers as they match the front panel as reasonably as possible
- everything necessary to power the system should match `internal-*'`
- no need to include words that describe what the driver does, devices are matched by driver or protocol and then name
- `desc:` may be implemented in the future for a more readable name.
