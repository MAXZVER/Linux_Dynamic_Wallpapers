#!/bin/bash
python_path=$(which python3)
time_zone_script_path=$(pwd)/"timezone_walpaper.py"

crontab -l > new_crone
echo "01 12 * * * env DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus $python_path $time_zone_script_path" >> new_crone
crontab new_crone
rm new_crone

