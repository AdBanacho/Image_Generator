from os.path import dirname
from pathlib import Path

import cv2
import numpy as np
import streamlit as st

from PIL import Image

from configuration_config import choose_config, display_config, to_config_file, update_config
from run_generator import run_generator


def sidebar(exist_choice):
    st.sidebar.title("Images generator")
    items_options = []
    st.sidebar.header("Items settings")
    items_options.append(st.sidebar.checkbox("Delete existing items", False))
    items_options.append(
        st.sidebar.number_input("How many transformed items have to be created per one loaded item?", 0, None, 2000, 1)
    )
    background_options = []
    st.sidebar.header("Background settings")
    background_options.append(st.sidebar.checkbox("Delete existing backgrounds", False))
    background_options.append(
        st.sidebar.number_input("How many background images have to be download per one category?", 0, None, 200, 1)
    )
    results_options = []
    st.sidebar.header("Result photos settings")
    results_options.append(st.sidebar.checkbox("Delete existing results", False))
    results_options.append(st.sidebar.number_input("How many result images have to be created?", 0, None, 2000, 1))
    if not exist_choice:
        results_options.append(st.sidebar.number_input("Height of result photo?", 0, None, 416, 1))
        results_options.append(st.sidebar.number_input("Width of result photo", 0, None, 416, 1))
    options = [items_options, background_options, results_options]

    return options


def load_image(key, default_choice):
    uploaded_file = st.file_uploader("Upload file", type="png", key=key)
    name_of_item = ""
    if uploaded_file:
        uploaded_file = Image.open(uploaded_file)
        if not default_choice:
            name_of_item = st.text_input("Name of item", value="", key=key)
        else:
            name_of_item = f"Item_{key}"
        uploaded_file = np.asarray(uploaded_file, dtype=np.uint8)
        if st.checkbox("Display image", False, key=key):
            resized_image = cv2.resize(uploaded_file, dsize=(700, 300))
            st.image(resized_image, caption="Uploaded Image.")

    return uploaded_file, name_of_item


def transforming_panel():
    transformations = st.multiselect(
        "Which transform do you want to use?",
        ["Affine (Rotation, Shear, Scale)", "Perspective", "Contrast", "Brightness", "Translation"],
    )
    brightness = []
    affine = []
    perspective = []
    contrast = []
    translation = []
    for no_of_transformation in range(len(transformations)):
        if transformations[no_of_transformation] == "Brightness":
            st.header("Brightness")
            brightness.append(st.slider("How many items have to change the brightness(%)", 0, 100, 60, 1))
            brightness.append(st.slider("Random brightness between -x and x", 0, 255, 70, 1))
        elif transformations[no_of_transformation] == "Affine (Rotation, Shear, Scale)":
            st.header("Affine (Rotation, Shear, Scale)")
            affine.append(st.slider("How many items have to rotation(%)", 0, 100, 25, 1))
            affine.append(st.slider("Random rotation between -x and x degrees(80% of choose images)", 0, 180, 90, 1))
            affine.append(st.slider("Random rotation between -x and x (20% of choose images)", 0, 180, 180, 1))
            affine.append(st.slider("How many items have to shear(%)", 0, 100, 100, 1))
            affine.append(st.slider("Random shear between -x and x degrees", 0, 90, 45, 1))
            affine.append(st.slider("How many items have to scale(%)", 0, 100, 100, 1))
            affine.append(st.slider("Random scale between x-1 and x", 1.0, 2.0, 1.5, 0.1))
        elif transformations[no_of_transformation] == "Perspective":
            st.header("Perspective")
            st.info("Max scale bigger than 0.11 lead to multiple usage of perspective transform with scale 0.11")
            perspective.append(st.slider("How many items have to scale perspective(%)", 0, 100, 50, 1))
            perspective.append(st.slider("Random perspective scale min", 0.0, 0.1, 0.1, 0.005))
            perspective.append(st.slider("Random perspective scale max", 0.0, 0.13, 0.13, 0.005))
            if perspective[1] >= perspective[2]:
                st.warning("scale min >= max")
            if 0.11 < perspective[2] <= 0.12:
                st.info("Transform will be use 2 times with max scale 0.11")
            elif 0.12 < perspective[2]:
                st.info("Transform will be use 3 times with max scale 0.11")

        elif transformations[no_of_transformation] == "Contrast":
            st.header("Contrast")
            contrast.append(st.slider("How many items have to change contrast(%)", 0, 100, 100, 1))
            contrast.append(st.slider("Random contrast scale between x-1 and x", 1.0, 2.0, 1.5, 0.1))
        elif transformations[no_of_transformation] == "Translation":
            st.header("Translation")
            translation.append(st.slider("How many items have to translation a side(%)", 0, 100, 5, 1))
            translation.append(st.slider("Random translation scale between -x and x", 0.0, 0.3, 0.2, 0.05))

    transform_list = [brightness, affine, perspective, contrast, translation]
    return transform_list


def item_load(default_choice, exist_choice):
    st.set_option("deprecation.showfileUploaderEncoding", False)
    st.markdown("""# Item transforming""")
    item_count = st.number_input("How many items to load?", 1, 4, 1, 1)
    uploaded_files = []
    names_of_items = []
    for no_of_item in range(item_count):
        uploaded_file, name_of_item = load_image(no_of_item, default_choice)
        uploaded_files.append(uploaded_file)
        names_of_items.append(name_of_item)
    path_of_items = Path(dirname(__file__)) / "items"
    if not default_choice and not exist_choice:
        path_of_items = st.text_input("Path to save transformed items", value=f"{path_of_items}")
        transform_list = transforming_panel()
    else:
        transform_list = [
            [60, 70],
            [25, 90, 180, 100, 45, 100, 1.5],
            [100, 0.1, 0.11],
            [100, 1.5],
            [20, 0.15],
        ]
    return transform_list, uploaded_files, path_of_items, names_of_items


def background_load(default_choice):
    st.markdown("""# Background downloading""")
    category_count = st.number_input("How many categories of downloading images?", 1, 10, 1, 1)
    default_categories = [
        "street",
        "cafe",
        "Supermarket",
        "restaurant",
        "shop",
        "cup",
        "television",
        "cat",
        "dog",
        "laptop",
    ]
    category = default_categories[:category_count]
    path_of_backgrounds = Path(dirname(__file__)) / "backgrounds"
    if not default_choice:
        category = []
        for no_of_category in range(category_count):
            category.append(
                st.text_input("category: ", value=f"{default_categories[no_of_category]}", key=no_of_category)
            )
        path_of_backgrounds = st.text_input("Path to save backgrounds", value=f"{path_of_backgrounds}")

    return path_of_backgrounds, category


def run():
    path_of_config, default_choice, exist_choice = choose_config()
    options = sidebar(exist_choice)
    transform_list, uploaded_files, path_of_items, names_of_items = item_load(default_choice, exist_choice)
    if not exist_choice:
        path_of_backgrounds, category = background_load(default_choice)
    st.markdown("""# Creating results""")
    path_of_results = Path(dirname(__file__)) / "data"
    if not default_choice and not exist_choice:
        path_of_results = st.text_input("Path to save transformed results", value=f"{path_of_results}")
    elif default_choice:
        if st.checkbox("Display config", False):
            display_config(
                transform_list,
                path_of_items,
                names_of_items,
                path_of_backgrounds,
                category,
                path_of_results,
                path_of_config,
            )
    for no_of_item in range(len(uploaded_files)):
        if not names_of_items:
            st.warning(f"Missing name of item{no_of_item}")
    run_downloading, run_transforming, run_creating, run_resizing = False, False, False, False
    to_do = st.multiselect(
        "What to do?", ["Downloading backgrounds", "Transforming items", "Creating results photos", "Resizing photos"]
    )

    if st.button("Run generator"):
        if not exist_choice:
            to_config_file(
                options,
                transform_list,
                path_of_items,
                names_of_items,
                path_of_backgrounds,
                category,
                path_of_results,
                path_of_config,
            )
        else:
            update_config(options, names_of_items, path_of_config)

        for no_of_to_do in range(len(to_do)):
            if to_do[no_of_to_do] == "Downloading backgrounds":
                run_downloading = True
            elif to_do[no_of_to_do] == "Transforming items":
                if uploaded_files[0] is None:
                    st.warning("Item/Items did not load!")
                else:
                    run_transforming = True
            elif to_do[no_of_to_do] == "Creating results photos":
                run_creating = True
            elif to_do[no_of_to_do] == "Resizing photos":
                run_resizing = True
        with st.spinner("Processing..."):
            run_generator(run_downloading, run_transforming, run_creating, run_resizing, uploaded_files, path_of_config)
        st.success("Done!")


run()
