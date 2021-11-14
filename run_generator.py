from configparser import ConfigParser

from background import generate_backgrounds
from images_generator import generate_items
from overfitting import generate_data
from yolodata import YoloData


def list_from_config(data_from_config):
    list_of_string = data_from_config[1:-1].split(", ")
    for i in range(len(list_of_string)):
        list_of_string[i] = list_of_string[i][1:-1]
    return list_of_string


def run_generator(run_downloading, run_transforming, run_creating, run_resizing, uploaded_files, path_of_config):

    config_object = ConfigParser()
    try:
        config_object.read(path_of_config)
    except Exception:
        raise Warning("Not found config")
    item_config = config_object["ITEM"]
    background_config = config_object["BACKGROUND"]
    data_config = config_object["DATA"]

    if run_downloading:
        generate_backgrounds(
            path_of_backgrounds=background_config["path_of_background"],
            backgrounds_count=background_config.getint("backgrounds_count_per_category"),
            categories=list_from_config(background_config["categories"]),
            delete=background_config.getboolean("delete"),
        )
    if run_transforming:
        generate_items(
            uploaded_files=uploaded_files,
            path_of_item=item_config["path_of_item"],
            items_count=item_config.getint("items_count_per_name"),
            names_of_items=list_from_config(item_config["names_of_item"]),
            delete=item_config.getboolean("delete"),
            path_of_config=path_of_config,
        )
    if run_creating:
        generate_data(
            path_of_item=item_config["path_of_item"],
            path_of_backgrounds=background_config["path_of_background"],
            path_of_data=data_config["path_of_data"],
            categories=list_from_config(background_config["categories"]),
            names_of_items=list_from_config(item_config["names_of_item"]),
            results_count=data_config.getint("results_count"),
            delete=data_config.getboolean("delete"),
        )
    if run_resizing:

        yolo_data = YoloData(
            target_height=data_config.getint("target_height"),
            target_width=data_config.getint("target_width"),
            path_of_data=data_config["path_of_data"],
            names_of_items=list_from_config(item_config["names_of_item"]),
        )
        yolo_data.resize()
        yolo_data.draw_boxes()
        yolo_data.labeling()
