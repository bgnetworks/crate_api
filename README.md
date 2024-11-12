# CRATE Application Programming Interface

The CRATE API is implemented as a colleciton of [labgrid](https://github.com/labgrid-project/labgrid) resources and drivers. These can be called as a library as shown in `crate_api/example.py`.

The `crate_api/create-x6-v1.yaml` labgrid environment file specifies the specific hardware configuration for the 6-channel revision 1 CRATE.

## Linux Installation
Create a python virtual environment:

`cd crate_sdk/crate_api`

`python3 -m venv venv_crate_api && source venv_crate_api/bin/activate`

Install python dependencies:

`pip3 install .`

Additionally, the CAN and Ethernet interface configuration drivers included in this repository currently call `sudo ip ...` to configure the interfaces, which requires the user to have sudo permission for the ip command.

## Windows Installation
Download Python3: https://www.python.org/downloads/
Download PEAK System Drivers: https://www.peak-system.com/quick/DrvSetup

Create a python virtual environment from Git Bash:
`/path/to/python3 -m venv crate_api_venv && source crate_api_venv/Scripts/activate`

Acquire pip library files. These should be packaged with the release, if not please consult your contact at BGN
* wabgrid-<VERSION>-py3-none-any.whl

Install required python packages
```
pip install wabgrid-<VERSION>-py3-none-any.whl
```

## Example Execution

`cd crate_api/examples && python example.py`
