
sensor_monitoring
=================

Some project.

**Tested on**:
python 3.8
Kubuntu 20LTS

**install**:
```
cd <project_dir>
python3 -m venv .env
source .env/bin/activate
pip install git+git://github.com/sergej-i/sensor_monitoring
```

**Run**:
sensor_monitor.py

**Config**
<project_dir>/.env/bin/sensor_monitoring_config/monitoring.json

**Codestyle**:
```
pylint -d C0103,R0903 *.py
pylint -d C0103,R0903 sensor_monitoring/*.py
or (without TODO)
pylint -d C0103,R0903,W0511 *.py
pylint -d C0103,R0903,W0511 sensor_monitoring/*.py
```
