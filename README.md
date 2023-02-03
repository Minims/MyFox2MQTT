# MyFox2MQTT

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/minims)

MyFox to MQTT

Supported :

- Myfox Home Control 2 ✅
- Evology Zen ✅
- Myfox Home Control Pro (To validate)
- Easy Box (To Validate)

https://api.myfox.me

## What is Working

- Alarm Control Panel in HA
  - arm_away
  - arm_night
  - alarm status
- Some devices are exposed in HA with their configuration

## TODO

- Retrieve Data from specific devices such as PIR (Include Temperature Sensor)
- Sockets
- Shutters
- ...

## Installation

### Requirements

- A Client ID & a Client Secret

Go to [myfox API Authentication](https://api.myfox.me/dev/authentication),
Click on create on \*First step is to create your own personnal\*\*.
`Client ID` and `Client Secret` can be found at [myfox API - My Applications](https://api.myfox.me/dev/apps).

- Use a myfox dedicated user for homeassistant.
- This dedicated user must be declared as a owner, not a child.
- HA MQTT integration must be reconfigure with MQTT Discovery.
- In the config file, check that you have set the name of your house. (The one define in the MyFox App.)

```
sites:
  - Maison
```

### Easy Mode (via HomeAssistant Supervisor)

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FMinims%2Fhomeassistant-addons)

In HomeAssistant, go to Supervisor > Add-on Store > Repositories
Add this repo: https://github.com/minims/homeassistant-addons/

Configure it with you credentials
Then all Devices will appaears in MQTT integration

### Easy Mode (Running in Docker Container)

Add docker container `docker run -v <PATH-TO-CONFIG-FOLDER>:/config minims/myfox2mqtt`

Add config to `<PATH-TO-CONFIG-FOLDER>`

### Manual Mode

Clone the repo
Go to dev branch

```
cd /opt/
git clone https://github.com/Minims/MyFox2MQTT.git
git checkout dev # if you want the dev branch
cd /opt/MyFox2MQTT/
```

Install Python3 dependencies

```
pip3 install -r  myFox2Mqtt/requirements.txt
```

Copy config file and setup your own credentials for MyFox & MQTT.

```
cd /opt/MyFox2MQTT/myFox2Mqtt
cp config/config.yaml.example config/config.yaml
```

## Running

```
cd MyFox2MQTT/myFox2Mqtt
python3 main.py
```

## Systemd (Running in background on boot)

## 5. (Optional) Running as a daemon with systemctl

To run MyFox2MQTT as daemon (in background) and start it automatically on boot we will run MyFox2MQTT with systemctl.

```bash
# Create a systemctl configuration file for MyFox2MQTT
sudo nano /etc/systemd/system/myFox2mqtt.service
```

Add the following to this file:

```
[Unit]
Description=myFox2mqtt
After=network.target

[Service]
WorkingDirectory=/opt/MyFox2MQTT/myFox2Mqtt
ExecStart=/usr/bin/python3 /opt/MyFox2MQTT/myFox2Mqtt/main.py
StandardOutput=inherit
# Or use StandardOutput=null if you don't want MyFox2MQTT messages filling syslog, for more options see systemd.exec(5)
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

Save the file and exit.

Verify that the configuration works:

```bash
# Start MyFox2MQTT
sudo systemctl start myFox2mqtt

# Show status
systemctl status myFox2mqtt.service
```

Now that everything works, we want systemctl to start MyFox2MQTT automatically on boot, this can be done by executing:

```bash
sudo systemctl enable myFox2mqtt.service
```

Done! 😃

Some tips that can be handy later:

```bash
# Stopping MyFox2MQTT
sudo systemctl stop myFox2mqtt

# Starting MyFox2MQTT
sudo systemctl start myFox2mqtt

# View the log of MyFox2MQTT
sudo journalctl -u myFox2mqtt.service -f
```

## Developement

This code is base on reverse engineering of the Android Mobile App.

- https://apkgk.com/APK-Downloader?package=com.myfox.android.mss
- Decompilation : https://github.com/google/enjarify

```
python3 -O -m enjarify.main ../com-myfox-android-mss1610600400.apk
ls
com-myfox-android-mss1610600400-enjarify.jar
```

- Open JAR and Get Java Code (JD-UI) : https://github.com/java-decompiler/jd-gui/releases

So if you want to contribue, have knowledge in JAVA / APK, you can help to find all API calls used in the APP.

- Use APKTool to get smali files and all available API Endpoints
