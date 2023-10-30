import copy
import json
import math
import xml.etree.ElementTree as ElementTree
import datetime
import os.path
import uuid
import shutil

from pathlib import Path
from astral.sun import sun as astral_sun
from astral import LocationInfo


def create_static_element(root_element, path_to_image, duration):
    static_element = ElementTree.Element("static")

    file_element = ElementTree.SubElement(static_element, "file")
    file_element.text = str(path_to_image)

    duration_element = ElementTree.SubElement(static_element, "duration")
    duration_element.text = str(duration)

    root_element.append(static_element)


def create_start_time_section(root_element):
    starttime_element = ElementTree.Element("starttime")

    year_element = ElementTree.SubElement(starttime_element, "year")
    year_element.text = str(datetime.date.today().year)

    mouth_element = ElementTree.SubElement(starttime_element, "month")
    mouth_element.text = "1"

    day_element = ElementTree.SubElement(starttime_element, "day")
    day_element.text = "1"

    hour_element = ElementTree.SubElement(starttime_element, "hour")
    hour_element.text = "0"

    minute_element = ElementTree.SubElement(starttime_element, "minute")
    minute_element.text = "0"

    second_element = ElementTree.SubElement(starttime_element, "second")
    second_element.text = "0"

    root_element.append(starttime_element)


def indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


if __name__ == '__main__':
    # Load config file

    path_to_script_dir = os.path.realpath(os.path.dirname(os.path.abspath(__file__)))

    standard_config_path = Path(path_to_script_dir) / "config.json"
    json_file = open(standard_config_path, "rb")
    json_data = json.load(json_file)
    json_file.close()

    # Set command wallpaper set
    if json_data["old_ubuntu"]:
        command_set_wallpaper = "gsettings set org.gnome.desktop.background picture-uri" + " file://"
    else:
        command_set_wallpaper = "gsettings set org.gnome.desktop.background " + json_data["theme"] + " file://"

    root_element = ElementTree.Element("background")
    create_start_time_section(root_element)

    path_to_image_dir = os.path.join(path_to_script_dir, json_data["image_dir"])
    list_images = os.listdir(path_to_image_dir)
    list_images.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))

    all_available_backgrounds = len(list_images)

    # Create work dir for create new xml file
    work_dir = Path(os.path.dirname(os.path.abspath(__file__))) / "work_dir"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir()

    # Set new xnl path
    path_of_new_xml = work_dir / (str(uuid.uuid4().hex) + ".xml")

    # Calculate time for sunset and sunrise

    city = LocationInfo(json_data["city"], json_data["country"], json_data["timezone"], json_data["latitude"],
                        json_data["longitude"])
    sun = astral_sun(city.observer, date=datetime.datetime.now())
    today = datetime.datetime.now()
    new_day = today.replace(hour=0, minute=0, second=0, microsecond=0)

    sun_is_down_new_day = math.ceil(sun['dawn'].timestamp() - new_day.timestamp())
    sun_is_up = math.ceil(sun['dusk'].timestamp() - sun['dawn'].timestamp())

    # Segment of change image
    sun_is_up_time_segment = math.ceil(sun_is_up / (all_available_backgrounds - 1))

    sun_is_down_old_day = 24 * 60 * 60 - sun_is_down_new_day - sun_is_up_time_segment * (all_available_backgrounds - 1)

    create_static_element(root_element, os.path.join(path_to_image_dir, list_images[-1]), sun_is_down_new_day)
    for image in list_images[:-1]:
        create_static_element(root_element, os.path.join(path_to_image_dir, image), sun_is_up_time_segment)
    create_static_element(root_element, os.path.join(path_to_image_dir, list_images[-1]), sun_is_down_old_day)

    # Write new xml file
    indent(root_element)
    str_data = ElementTree.tostring(root_element)

    xml_file = open(path_of_new_xml, "wb")
    xml_file.write(str_data)
    xml_file.close()

    command_set_wallpaper += str(path_of_new_xml)

    # Set new wallpaper xml
    os.system(command_set_wallpaper)
