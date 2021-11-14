from configparser import ConfigParser

import cv2
import numpy as np

from imgaug import augmenters as iaa


def list_from_config(data_from_config):
    list_of_int = data_from_config[1:-1].split(", ")
    return list_of_int


def brightness(images, path_of_config):
    config_object = ConfigParser()
    config_object.read(path_of_config)
    transformation_config = config_object["TRANSFORMATIONS"]
    if len(transformation_config["brightness"]) > 2:
        brightness_chance = int(list_from_config(transformation_config["brightness"])[0])
        brightness_scale = int(list_from_config(transformation_config["brightness"])[1])
        if np.random.randint(0, 100) <= brightness_chance:
            brightness_level = np.random.randint(-brightness_scale, brightness_scale, (images.shape[0], 1, 1, 1))
            brightness_value = np.zeros((*images.shape[:3], 4))
            brightness_value[:, :, :, :-1] = brightness_level
            images += brightness_value
            images[images > 255] = 255
            images[images < 0] = 0

    return images


def perspective(perspective_list):
    times = 1
    perspective_list[1] = float(perspective_list[1])
    perspective_list[2] = float(perspective_list[2])
    if 0.11 < perspective_list[2] <= 0.12:
        perspective_list[2] = 0.11
        times = 2
    elif 0.12 < perspective_list[2]:
        perspective_list[2] = 0.11
        times = 3
    return iaa.SomeOf(
        times,
        [
            iaa.PerspectiveTransform(scale=(perspective_list[1], perspective_list[2]), fit_output=True),
            iaa.PerspectiveTransform(scale=(perspective_list[1], perspective_list[2]), fit_output=True),
            iaa.PerspectiveTransform(scale=(perspective_list[1], perspective_list[2]), fit_output=True),
        ],
    )


def contrast(contrast_value):
    return iaa.OneOf(
        [
            iaa.GammaContrast((contrast_value - 1, contrast_value)),
            iaa.SigmoidContrast(gain=(3, 10), cutoff=(contrast_value - 1, contrast_value - 0.75)),
            iaa.LogContrast(gain=(contrast_value - 1, contrast_value)),
            iaa.LinearContrast((contrast_value - 1, contrast_value)),
        ]
    )


def transformations_of_images(path_of_config):
    config_object = ConfigParser()
    config_object.read(path_of_config)
    transformation_config = config_object["TRANSFORMATIONS"]
    if len(transformation_config["affine"]) > 2:
        affine_list = list_from_config(transformation_config["affine"])
    else:
        affine_list = [0.0, 90, 180, 0.0, 45, 0.0, 1.5]
    if len(transformation_config["perspective"]) > 2:
        perspective_list = list_from_config(transformation_config["perspective"])
    else:
        perspective_list = [0.0, 0.015, 0.1]
    if len(transformation_config["translation"]) > 2:
        translation_list = list_from_config(transformation_config["translation"])
    else:
        translation_list = [0.0, 0.2]
    if len(transformation_config["contrast"]) > 2:
        contrast_list = list_from_config(transformation_config["contrast"])
    else:
        contrast_list = [0.0, 1.5]

    return iaa.Sequential(
        [
            iaa.Sometimes(float(contrast_list[0]) / 100, contrast(float(contrast_list[1]))),
            iaa.Sometimes(
                float(affine_list[0]) / 100,
                iaa.Sometimes(
                    0.2,
                    iaa.Affine(rotate=(-int(affine_list[2]), int(affine_list[2]))),
                    iaa.Affine(rotate=(-int(affine_list[1]), int(affine_list[1]))),
                ),
            ),
            iaa.Sometimes(
                float(affine_list[3]) / 100,
                iaa.Affine(shear=(-int(affine_list[4]), int(affine_list[4])), fit_output=True),
            ),
            iaa.Sometimes(
                float(affine_list[5]) / 100,
                iaa.Affine(scale=(float(affine_list[6]), float(affine_list[6])), fit_output=True),
            ),
            iaa.Sometimes(
                float(perspective_list[0]) / 100,
                perspective(perspective_list),
            ),
            iaa.Sometimes(
                float(translation_list[0]) / 100,
                iaa.Affine(
                    translate_percent={
                        "x": (-float(translation_list[1]), float(translation_list[1])),
                        "y": (-float(translation_list[1]), float(translation_list[1])),
                    }
                ),
            ),
        ],
        random_order=False,
    )


def scale(background_shape, item):
    scale_norm = np.random.normal(0.35, 0.2)
    if scale_norm < 0.15:
        scale_norm = 0.15
    height = int(scale_norm * background_shape[0])
    width = int(scale_norm * background_shape[1])
    return cv2.resize(item, dsize=(width, height))


def cut_blank_place(image):
    min_width_of_item = 0
    min_height_of_item = 0
    max_width_of_item = image.shape[1]
    max_height_of_item = image.shape[0]
    for h in range(image.shape[0]):
        if any(image[h, :, 3] > 100):
            min_height_of_item = h
            break
    for w in range(image.shape[1]):
        if any(image[:, w, 3] > 100):
            min_width_of_item = w
            break
    for h in range(image.shape[0] - 1, 0, -1):
        if any(image[h, :, 3] > 100):
            max_height_of_item = h
            break
    for w in range(image.shape[1] - 1, 0, -1):
        if any(image[:, w, 3] > 100):
            max_width_of_item = w
            break
    cut_image = image[min_height_of_item:max_height_of_item, min_width_of_item:max_width_of_item, :]
    return cut_image.astype(np.uint8)
