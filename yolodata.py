import copy
import shutil

from pathlib import Path

import cv2
import numpy as np

from PIL import Image


def draw_box(box_shape, corner, image, no_of_item):
    girth = 3
    if box_shape[0][no_of_item] == 0:
        color = (255, 0, 0)
    elif box_shape[0][no_of_item] == 1:
        color = (0, 255, 0)
    elif box_shape[0][no_of_item] == 2:
        color = (0, 0, 255)
    else:
        color = (255, 255, 255)

    h = corner[0][no_of_item]
    w = corner[1][no_of_item]
    height_line = corner[0][no_of_item] + box_shape[4][no_of_item]
    width_line = corner[1][no_of_item] + box_shape[3][no_of_item]
    girth_height_line_min = corner[0][no_of_item] + girth
    girth_width_line_min = corner[1][no_of_item] + girth
    girth_height_line_max = corner[0][no_of_item] + box_shape[4][no_of_item] - girth
    girth_width_line_max = corner[1][no_of_item] + box_shape[3][no_of_item] - girth
    image[h:height_line, w:girth_width_line_min, :] = color
    image[h:height_line, girth_width_line_max:width_line, :] = color
    image[h:girth_height_line_min, w:width_line, :] = color
    image[girth_height_line_max:height_line, w:width_line, :] = color
    return image


def positions_of_boxes(box_shape, list_of_txt, names_of_items, image_shape):
    box_shape[0] = np.genfromtxt(list_of_txt, usecols=0)
    for shape in range(1, 5):
        box_shape[shape] = np.round(np.genfromtxt(list_of_txt, usecols=shape) * image_shape)
    corner = np.zeros((2, len(names_of_items)))
    corner[1] = box_shape[1] - box_shape[3] // 2
    corner[0] = box_shape[2] - box_shape[4] // 2
    corner[corner < 0] = 0
    return box_shape.astype(int), corner.astype(int)


class YoloData:
    def __init__(self, target_height, target_width, path_of_data, names_of_items):
        self.target_height = target_height
        self.target_width = target_width
        self.names_of_items = names_of_items
        self.path_of_data = Path(path_of_data)
        self.path_of_results = self.path_of_data / "results"
        self.path_of_resized_results = self.path_of_data / "results_resized"
        self.path_of_boxed_results = self.path_of_data / "results_resized_boxed"

    def resize(self):
        list_of_image = list(self.path_of_results.glob("**/*.jpg"))
        list_of_txt = list(self.path_of_results.glob("**/*.txt"))
        if not self.path_of_resized_results.is_dir():
            self.path_of_resized_results.mkdir()
        if not (self.path_of_resized_results / "images").is_dir():
            (self.path_of_resized_results / "images").mkdir()
        if not (self.path_of_resized_results / "labels").is_dir():
            (self.path_of_resized_results / "labels").mkdir()
        for no_of_image in range(len(list_of_image)):
            image = Image.open(list_of_image[no_of_image])
            image = np.asarray(image, dtype=np.uint8)
            image = cv2.resize(
                image,
                dsize=(self.target_width, self.target_height),
            )
            image = Image.fromarray(image)
            image.save(self.path_of_resized_results / "images" / f"Photo_{no_of_image + 1}.jpg")
            shutil.copy(
                list_of_txt[no_of_image], self.path_of_resized_results / "labels" / f"Photo_{no_of_image + 1}.txt"
            )

    def draw_boxes(self):
        list_of_image = list(self.path_of_resized_results.glob("**/*.jpg"))
        list_of_txt = list(self.path_of_resized_results.glob("**/*.txt"))
        if not self.path_of_boxed_results.is_dir():
            self.path_of_boxed_results.mkdir()
        for no_of_image in range(len(list_of_image)):
            box_shape = np.zeros((5, len(self.names_of_items)))
            image = Image.open(list_of_image[no_of_image])
            image = np.asarray(image, dtype=np.uint8)
            box_shape, corner = positions_of_boxes(
                box_shape, list_of_txt[no_of_image], self.names_of_items, image.shape[0]
            )
            boxed_image = copy.deepcopy(image)
            for no_of_item in range(len(self.names_of_items)):
                boxed_image = draw_box(box_shape, corner, boxed_image, no_of_item)
            boxed_image = Image.fromarray(boxed_image)
            boxed_image.save(self.path_of_boxed_results / f"Photo_{no_of_image + 1}.jpg")

    def write_list_to_file(self, list_of_names, path_of_save, name_of_file):
        file = open(path_of_save / name_of_file, "w")
        for no_of_name in range(len(list_of_names)):
            file.write(f"{list_of_names[no_of_name]}\n")
        file.close()

    def labeling(self):
        path_of_colab = "data/items"
        path_of_photos = self.path_of_resized_results / "images"
        names_of_train = []
        names_of_valid = []
        list_of_images = list(path_of_photos.glob("**/*.jpg"))
        for no_of_photos in range(len(list_of_images)):

            if no_of_photos < len(list_of_images) * 0.8:
                names_of_train.append("{}Photo_{}.jpg".format(path_of_colab + "/images/", no_of_photos + 1))
                # names_of_train.append(list_of_images[no_of_photos])
            else:
                names_of_valid.append("{}Photo_{}.jpg".format(path_of_colab + "/images/", no_of_photos + 1))
                # names_of_valid.append(list_of_images[no_of_photos])
        self.write_list_to_file(names_of_train, self.path_of_data, "train.txt")
        self.write_list_to_file(names_of_valid, self.path_of_data, "valid.txt")
        self.write_list_to_file(self.names_of_items, self.path_of_data, "data.name")

        file = open(self.path_of_data / "data.data", "w")
        file.write(f"classes = {len(self.names_of_items)}\n")
        file.write("train = {}\n".format("data/train.txt"))
        file.write("valid = {}\n".format("data/valid.txt"))
        file.write("names = {}\n".format("data/data.name"))
        file.close()
