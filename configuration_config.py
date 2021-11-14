from configparser import ConfigParser
from os.path import dirname
from pathlib import Path

import streamlit as st


def to_config_file(
    options,
    transform_list,
    path_of_items,
    names_of_items,
    path_of_backgrounds,
    category,
    path_of_results,
    name_of_config,
):
    config_object = ConfigParser()
    config_object["ITEM"] = {
        "path_of_item": str(path_of_items),
        "names_of_item": str(names_of_items),
        "items_count_per_name": str(options[0][1]),
        "delete": str(options[0][0]),
    }

    config_object["TRANSFORMATIONS"] = {
        "list_of_transform": str(transform_list),
        "brightness": str(transform_list[0]),
        "affine": str(transform_list[1]),
        "perspective": str(transform_list[2]),
        "contrast": str(transform_list[3]),
        "translation": str(transform_list[4]),
    }

    config_object["BACKGROUND"] = {
        "path_of_background": str(path_of_backgrounds),
        "categories": str(category),
        "backgrounds_count_per_category": str(options[1][1]),
        "delete": str(options[1][0]),
    }

    config_object["DATA"] = {
        "path_of_data": str(path_of_results),
        "target_height": str(options[2][2]),
        "target_width": str(options[2][3]),
        "results_count": str(options[2][1]),
        "delete": str(options[2][0]),
    }

    with open(f"{name_of_config}", "w") as conf:
        config_object.write(conf)


def display_config(
    transform_list,
    path_of_items,
    names_of_items,
    path_of_backgrounds,
    category,
    path_of_results,
    name_of_config,
):
    st.info(f"Config: {name_of_config}")
    st.write(f"Path to save items: {path_of_items}")
    st.write(f"Names of items: {names_of_items}")
    st.write(f"Path to save background: {path_of_backgrounds}")
    st.write(f"Categories: {category}\n")
    st.write(f"Path to save results: {path_of_results}")
    st.info("Brightness")
    st.write(f" Percent item transform of brightness: {transform_list[0][0]}%")
    st.write(f"Brightness value randomly between: [-{transform_list[0][1]}, {transform_list[0][1]}]")
    st.info("Affine")
    st.write(f"Percent item transform of affine rotation: {transform_list[1][0]}%")
    st.write(
        f"//For 80% of {transform_list[1][0]}% items// Rotation value randomly between: "
        f"[-{transform_list[1][1]}, {transform_list[1][1]}]"
    )
    st.write(
        f"//For 20% of {transform_list[1][0]}% items// Rotation value randomly between: "
        f"[-{transform_list[1][2]}, {transform_list[1][2]}]"
    )
    st.write(f"Percent item transform of affine shear: {transform_list[1][3]}%")
    st.write(f"Shear value randomly between: [-{transform_list[1][4]}, {transform_list[1][4]}]")
    st.write(f"Percent item transform of affine scale: {transform_list[1][5]}%")
    st.write(f"Scale value randomly between: [{transform_list[1][6] - 1}, {transform_list[1][6]}]")
    st.write(f"Percent item transform of affine scale: {transform_list[1][5]}%")
    st.write(f"Scale value randomly between: [{transform_list[1][6] - 1}, {transform_list[1][6]}]")
    st.info("Perspective")
    st.write(f" Percent item transform of perspective: {transform_list[2][0]}%")
    st.write(f"Piecewise value randomly between: [-{transform_list[2][1]}, {transform_list[2][2]}]")
    st.write(f"Perspective value randomly between: [-{transform_list[2][3]}, {transform_list[2][4]}]")
    st.info("Contrast")
    st.write(f"Percent item transform of contrast: {transform_list[3][0]}%")
    st.write(f"Contrast value randomly between: [-{transform_list[3][1] - 1}, {transform_list[3][1]}]")
    st.info("Translation one side")
    st.write(f"Percent item transform of Translation: {transform_list[4][0]}%")
    st.write(f"Translation value randomly between: [-{transform_list[4][1]}, {transform_list[4][1]}]")


def update_config(options, names_of_items, path_of_config):
    config_object = ConfigParser()
    config_object.read(path_of_config)
    config_item = config_object["ITEM"]

    config_item["names_of_item"] = str(names_of_items)
    config_item["items_count_per_name"] = str(options[0][1])
    config_item["delete"] = str(options[0][0])

    config_background = config_object["BACKGROUND"]
    config_background["backgrounds_count_per_category"] = str(options[1][1])
    config_background["delete"] = str(options[1][0])

    config_data = config_object["DATA"]
    config_data["results_count"] = str(options[2][1])
    config_data["delete"] = str(options[2][0])

    with open(path_of_config, "w") as conf:
        config_object.write(conf)


def choose_config():
    st.markdown("""# Config""")

    config_choice = st.selectbox("Choice config", ("Create new", "Default", "Use exist"))
    default_choice = False
    exist_choice = False
    if config_choice == "Default":
        default_choice = True
        path_of_config = "default_config.cfg"
    elif config_choice == "Create new":
        default_path_of_config = Path(dirname(__file__)) / "config.cfg"
        path_of_config = st.text_input("Path to save config.cfg", value=f"{default_path_of_config}")
    else:
        exist_choice = True
        default_path_of_config = Path(dirname(__file__)) / "config.cfg"
        path_of_config = st.text_input("Path to save config.cfg", value=f"{default_path_of_config}")

    return path_of_config, default_choice, exist_choice
