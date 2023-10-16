import copy
import json
import math
import xml.etree.ElementTree as ElementTree
import datetime
import os.path
import uuid
from pathlib import Path
import shutil

from astral import Astral


def set_duration(static_element, duration):
    for child_static in static_element:
        if child_static.tag == "duration":
            child_static.text = str(duration)


if __name__ == '__main__':
    # Load config file
    standard_config_path = Path(os.path.dirname(os.path.abspath(__file__))) / "config.json"
    json_file = open(standard_config_path, "rb")
    json_data = json.load(json_file)

    # Set command wallpaper set
    command_set_wallpaper = "gsettings set org.gnome.desktop.background " + json_data["theme"] + " file://"

    tree = ElementTree.parse(json_data["original_xml"])
    root = tree.getroot()

    # Count available backgrounds and find last wallpaper for night of new day
    all_available_backgrounds = 0
    first = False
    count_insert = 0
    for count, child in enumerate(root):
        if child.tag == "static":
            if not first:
                first = True
                count_insert = count
            all_available_backgrounds += 1
    # Copy last night element
    last_night_element = root[count_insert + all_available_backgrounds - 1]
    inserted_element = copy.deepcopy(root[count_insert + all_available_backgrounds - 1])

    # Create work dir for create new xml file
    work_dir = Path(os.path.dirname(os.path.abspath(__file__))) / "work_dir"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir()

    # Set new xnl path
    path_of_new_xml = work_dir / (str(uuid.uuid4().hex) + ".xml")

    # Calculate time for sunset and sunrise
    a = Astral()
    a.solar_depression = 'civil'
    city = a[json_data["city"]]
    sun = city.sun(date=datetime.datetime.now(), local=True)
    today = datetime.datetime.now()
    new_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
    sun_is_down_new_day = sun['dawn'].timestamp() - new_day.timestamp()
    sun_is_up = ((sun['dusk'] - sun['dawn']).total_seconds())

    # Segment of change image
    sun_is_up_time_segment = math.ceil(sun_is_up / (all_available_backgrounds - 1))

    sun_is_down_old_day = 24 * 60 * 60 - sun_is_down_new_day - sun_is_up_time_segment * (all_available_backgrounds - 1)

    for count, child in enumerate(root):
        if child.tag == "static":
            set_duration(child, sun_is_up_time_segment)

    # Set nighttime for last and first image
    set_duration(last_night_element, sun_is_down_old_day)
    set_duration(inserted_element, sun_is_down_new_day)

    # Insert in first position night new day image
    root.insert(count_insert, inserted_element)

    # Write new xml file
    tree.write(str(path_of_new_xml))

    command_set_wallpaper += str(path_of_new_xml)

    # Set new wallpaper xml
    os.system(command_set_wallpaper)
