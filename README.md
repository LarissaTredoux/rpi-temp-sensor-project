# Raspberry Pi Temperature Sensor Guide
The aim of this project is to build a network of Raspberry Pi's that can be connected to a range of different sensors. The Raspberry Pi's take measurements from the sensors and raise alarms accordingly when undesirable sensor values are detected (the measurements are above a certain temperature/humidity threshold or maybe there's smoke somewhere...)

The functionality is as follows:
  - Read values from sensors. Currently the sensors that are supported are: the DHT-11 Temperature and Humidity sensor, the Raspberry Pi's internal CPU temperature sensor, and the [Sensirion EK-H4] sensor with four nodes, each measuring temperature and humidity.
  - A [Prometheus Client] page for each Raspberry Pi showing recent values from each sensor.
  - A Telegram bot for each Raspberry Pi that sends alert messages when alarms go off. The Telegram bot also allows commands to change threshold values for sensors, or get the most recent measurements from the sensors.
  - A [YAML] configuration file for each Raspberry Pi that allows for changing alarm messages, sensor names, threshold values and more.
  - A peer check where each Raspberry Pi node checks if one or more other Raspberry Pi's are online.
  - Automatic startup when the Raspberry Pi boots.

This functionality is developed in Python. 

## How to use the functionality

### Setting up a new Raspberry Pi
The Raspberry Pi should have a working internet connection. 

First, you'll need to download the files onto a Raspberry Pi.

```
$ git clone https://github.com/LarissaTredoux/vastech-rpi-project.git
```

You'll need to install python packages for the [Telegram bot], [YAML] (`pip install pyyaml` is easiest) and [Prometheus Client].

The [Adafruit_DHT] package needs to be installed for the DHT-11 sensor. The YAML file needs to be edited according to your specific setup. For startup on boot, a [systemd] service file needs to be written with the following content:

```sh
1  [Unit]
2  Description=Raspberry Pi Temp Sensor
3  After=systemd-networkd-wait-online.service
4  Wants=systemd-networkd-wait-online.service
5 
6  [Service]
7  ExecStart=/usr/bin/python3 -u prom_cli.py
8  WorkingDirectory=/home/pi/vastech-rpi-project
9  StandardOutput=inherit
10 StandardError=inherit
11 Restart=always
12 User=pi
13 
14 [Install]
15 WantedBy=multi-user.target
```

The contents of this file can also be copied from the `rpiscript.service` file provided. The Raspberry Pi can be rebooted to start the service or it can be started with the command:

```
$ sudo systemctl start myscript.service
```

where `myscript.service` should be replaced with your service file's name. Or you can just call it `myscript.service` if you like.

You'll also need to give your Raspberry Pi a static IP address. Then your Prometheus Client page will be found at `ip:8000` e.g. `http://192.168.0.10:8000/`.


### Setting up a new telegram bot
Then, you'll need to set up a new [Telegram bot]. This should be done with the [BotFather], who will give you a token for your bot. You'll need to paste this token into the `vastech_bot.py` file wherever the comment `# Bot token` is found. The naming convention for the bots is `VASTechBotRPi#` where `#` represents the number index of the Raspberry Pi (starting at 1). The username for the bots has the convention `VASTech#Bot`. 

Use the command `/setdescription` in BotFather to set the description. The description of the existing bots is:

```
Sends alert messages when alarms go off from sensors measuring temperature
```

Similarly, it is recommended to use `/setabouttext` to change the about text to something like:

```
Bot for Raspberry Pi #. Sends alerts when alarms go off due to temperature sensors (e.g. server room overheats)
```

`temperature` can of course be replaced with whatever your sensor measures. 

You can use `/setuserpic` in BotFather to set the user pic of the bot to the VASTech logo. If you would like a commands menu for your bot to appear in Telegram when you type `/`, you can use `/setcommands` in BotFather to set the commands list to:

```
start - Start the bot
help - Get help with commands
get_measurements - Get latest sensor measurements
set_upper_threshold - Change the upper threshold for a sensor. Format: /set_upper_threshold sensor_index new_threshold
set_lower_threshold - Change the lower threshold for a sensor. Format: /set_lower_threshold sensor_index new_threshold
switch_off_server - Switch off a server. Format: /switch_off_server server_name
get_active_alarms - Get a list of all alarms currently active
```


### Using an existing Telegram bot
Bots can be used in private chats or in groups. If you want the bot to see all messages in a group (and not just the commands directed to it specifically using `@BotUsername` or replies to the bot's messages), give the bot Admin privileges. If you want the bot to be able to send you alarm messages, you will need to give the `/start` command (this happens in private chats anyway but you should do it in the group too). This will return the following message:

```
Hello. I will give you information about alarms that go off for the sensors. Your chat id is [chat_id]; please add this to the config file so I can send you messages.
```

Add the given chat id to the `rpi.yaml` config file.

Remember, if you're stuck at any point you can always give the bot the `/help` command, which will give you a list of commands and their formats.


### Alarms
Current supported alarms are:
- Peer Down - one of the peers has gone offline
- Sensor Down - one of the sensors on the Raspberry Pi is no longer functioning correctly
- Sensor Out of Bounds - one of the sensors on the Raspberry Pi has given 10 consecutive out of bounds values (below 0 or above 100).
- Over Threshold - one of the sensors on the Raspberry Pi has returned a measurement that is over the specified threshold.

To add a new alarm, you will need to add an alarm name and message at the applicable sensor or peer in the `rpi.yaml` config file, according to the format:

```
- message:
  - Sensor_name
  - ': message '
  - 'threshold value if applicable'
  - ' more message if applicable'
  name: Alarm_name
```

See existing YAML file for examples.

To add a new alarm, you'll need to add code to check if the alarm should be active to the `alarms.py` file. The `alarm_check()` method will need to be edited to include logic to check whether to raise, update or clear the alarm. The `send_notification()` method will need to be edited to add a new alarm notification category. Use the existing formats. If a new dictionary is created to hold active alarms, it will need to be added to the `get_alarms()` method.

### Adding a new sensor
You'll need to add a file called `get_[sensor_name]_[sensor_measurement].py` to the `sensors` folder. Inside this folder you should have Python code that reads measurements from your new sensor. Then you'll have to add this sensor as an option in the `sensor_detect.py` file and make sure it calls your measurement-getting function and returns the correct value.

### Additional information
The code is designed for a maximum of four sensors to be connected to one Raspberry Pi. If more than four sensors are connected, you will need to extend the length of the following arrays in the `alarms.py` file:

- `oob_count` (out of bounds count - how many consecutive times each sensor has gone out of bounds. Default is 0)
- `oob_state` (0 if the sensor is within bounds, 1 if it is out of bounds. Default is 0)
- `sensor_states_prev` (Previous states of the sensors. 1 means the sensor is up, 0 means it is down. Default is 1)
- `sensor_flags` (These flags get set if an alarm goes off for a sensor. 0 means the flag is not set, 1 means the flag is set. Default is 0)

Similarly, the code is designed for each Raspberry Pi to check the states of a maximum of two peers. If more than two peers need to be checked, the `peer_states_prev` array will need to be extended. This array shows the previous states of all the peers that need to be checked. 1 means the peer is up, 0 means it is down. Default is 1.

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

   [sensirion ek-h4]: <https://github.com/SiLab-Bonn/basil/blob/master/basil/HL/sensirion_ekh4.py>
   [yaml]: <https://github.com/yaml/pyyaml>
   [prometheus client]: <https://github.com/prometheus/client_python>
   [Adafruit_DHT]: <http://www.circuitbasics.com/how-to-set-up-the-dht11-humidity-sensor-on-the-raspberry-pi/>
   [systemd]: <https://www.raspberrypi.org/documentation/linux/usage/systemd.md>
   [telegram bot]: <https://github.com/python-telegram-bot/python-telegram-bot>
   [botfather]: <https://core.telegram.org/bots#6-botfather>
