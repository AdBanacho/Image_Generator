import copy
import shutil
import warnings

from pathlib import Path

import numpy as np

from PIL import Image

from images_transformation import scale


def results_to_path(path_of_data, delete):
    path_of_results = path_of_data / "results"
    path_of_segmentation = path_of_data / "segmentation"
    if delete and path_of_data.is_dir():
        shutil.rmtree(path_of_data)
    if not path_of_data.is_dir():
        path_of_data.mkdir()
    if not path_of_results.is_dir():
        path_of_results.mkdir()
    if not path_of_segmentation.is_dir():
        path_of_segmentation.mkdir()
    return path_of_results


def list_of_backgrounds_and_items(path_of_items, path_of_backgrounds, categories, names_of_items):
    backgrounds_list = []
    items_name_list = [0, 0]
    path_of_name = path_of_items / names_of_items[0]
    items_list = list(path_of_name.glob("**/*.png"))
    for no_of_item in range(1, len(names_of_items)):
        path_of_name = path_of_items / names_of_items[no_of_item]
        items_name_list += [
            no_of_item,
            len(list(path_of_name.glob("**/*.png"))) + items_name_list[no_of_item - 2],
        ]  # [name of item as number, where item begin in table item_list]
        items_list += list(path_of_name.glob("**/*.png"))
    for no_of_category in range(len(categories)):
        path_of_category = path_of_backgrounds / categories[no_of_category]
        backgrounds_list += list(path_of_category.glob("**/*.*g"))
    return items_list, backgrounds_list, items_name_list


def load_background_and_item(items_list, backgrounds_list, items_name_list, no_of_result):
    items = []
    random_item_count = np.random.randint(1, len(items_name_list) // 2 + 1)
    random_items_list = np.random.choice(len(items_name_list) // 2, random_item_count, replace=False)
    for no_of_item in range(random_item_count):
        item = Image.open(
            items_list[(no_of_result + items_name_list[2 * random_items_list[no_of_item] + 1]) % len(items_list)]
        )
        items.append(np.asarray(item, dtype=np.uint8))
    background = Image.open(backgrounds_list[no_of_result % len(backgrounds_list)])
    background = np.asarray(background, dtype=np.uint8)
    return items, background, random_items_list


def position_of_boxes_to_txt(
    path_of_results, scaled_items, result_image_shape, random_spots, crop_spots, name_of_photo
):
    file = open(path_of_results / f"Photo_{name_of_photo}.txt", "w")
    for no_of_item in range(len(scaled_items)):
        if crop_spots[no_of_item][4]:
            height = np.round(
                (scaled_items[no_of_item].shape[0] - crop_spots[no_of_item][0] - crop_spots[no_of_item][1])
                / result_image_shape[0],
                6,
            )
            width = np.round(
                (scaled_items[no_of_item].shape[1] - crop_spots[no_of_item][2] - crop_spots[no_of_item][3])
                / result_image_shape[1],
                6,
            )
            center_x = np.round(
                (
                    random_spots[no_of_item][1]
                    + (scaled_items[no_of_item].shape[1] - crop_spots[no_of_item][2] - crop_spots[no_of_item][3]) / 2
                )
                / result_image_shape[1],
                6,
            )
            center_y = np.round(
                (
                    random_spots[no_of_item][0]
                    + (scaled_items[no_of_item].shape[0] - crop_spots[no_of_item][0] - crop_spots[no_of_item][1]) / 2
                )
                / result_image_shape[0],
                6,
            )
            file.write(f"{int(random_spots[no_of_item][2])} {center_x} {center_y} {width} {height}\n")
    file.close()


def creating_scaled_item(background, items):
    scaled_items = []
    for no_of_item in range(len(items)):
        sequence_of_transform = scale(background.shape, items[no_of_item])
        scaled_items.append(sequence_of_transform)
    return scaled_items


def position_of_item(background, scaled_item):
    crop_spot = np.zeros(4)  # top, bot, left, right
    random_spot = np.zeros(2)  # height, width
    random_spot[0] = np.random.randint(
        -int(0.2 * scaled_item.shape[0]), background.shape[0] - int(0.8 * scaled_item.shape[0])
    )
    random_spot[1] = np.random.randint(
        -int(0.2 * scaled_item.shape[1]), background.shape[1] - int(0.8 * scaled_item.shape[1])
    )
    if random_spot[0] < 0:
        crop_spot[0] = -random_spot[0]
    elif background.shape[0] - scaled_item.shape[0] < random_spot[0]:
        crop_spot[1] = abs(background.shape[0] - random_spot[0] - scaled_item.shape[0])
    if random_spot[1] < 0:
        crop_spot[2] = -random_spot[1]
    elif random_spot[1] > background.shape[1] - scaled_item.shape[1]:
        crop_spot[3] = abs(background.shape[1] - random_spot[1] - scaled_item.shape[1])
    return crop_spot.astype(int), random_spot.astype(int)


def is_there_item(boxes, random_spot, scaled_item):
    for no_of_item in range(boxes.shape[0]):
        if (
            boxes[no_of_item][0] - scaled_item.shape[0] < random_spot[0] < boxes[no_of_item][0] + boxes[no_of_item][3]
            and boxes[no_of_item][1] - scaled_item.shape[1]
            < random_spot[1]
            < boxes[no_of_item][1] + boxes[no_of_item][4]
        ):
            return True

    return False


def choosing_random_place_for_items(background, scaled_items, random_boxes):
    repeat, repeat_to = 0, 15
    found_place = 1
    crop_spot, random_spot = position_of_item(background, scaled_items)
    while is_there_item(random_boxes, random_spot, scaled_items) and repeat < repeat_to:
        crop_spot, random_spot = position_of_item(background, scaled_items)
        repeat += 1
    if repeat == repeat_to or is_there_item(random_boxes, random_spot, scaled_items):
        found_place = 0
    return crop_spot, random_spot, found_place


def overlay_background_with_item(background, scaled_items, random_items_list):
    position_of_boxes = np.zeros((len(scaled_items), 5))
    crop_spots = np.zeros((len(scaled_items), 5))
    result_image = np.zeros((background.shape[0], background.shape[1], 4))
    result_image[:, :, :3] = copy.deepcopy(background)

    for no_of_item in range(len(scaled_items)):
        crop_spot, random_spot, found_place = choosing_random_place_for_items(
            background, scaled_items[no_of_item], position_of_boxes
        )
        position_of_boxes[no_of_item] = (
            random_spot[0],
            random_spot[1],
            random_items_list[no_of_item],
            scaled_items[no_of_item].shape[0],
            scaled_items[no_of_item].shape[1],
        )
        crop_spots[no_of_item][:4] = crop_spot
        crop_spots[no_of_item][4] = found_place
        if found_place:
            for height in range(crop_spot[0], scaled_items[no_of_item].shape[0] - crop_spot[1]):
                for width in range(crop_spot[2], scaled_items[no_of_item].shape[1] - crop_spot[3]):
                    if scaled_items[no_of_item][height][width][3] > 100:
                        result_image[random_spot[0] + height, random_spot[1] + width, :3] = scaled_items[no_of_item][
                            height, width, :-1
                        ]
                        result_image[random_spot[0] + height, random_spot[1] + width, 3] = (
                            random_items_list[no_of_item] + 1
                        )

    return np.asarray(result_image, dtype=np.uint8), position_of_boxes[:, :3], crop_spots


def segmentation_items(results_image, random_items_list, path_of_results, name_of_photo):
    color = np.array([[204, 153, 51], [51, 51, 205], [255, 255, 255], [51, 205, 128], [0, 255, 255]])
    segmentation_image = np.zeros(results_image.shape)
    segmentation_image = segmentation_image[:, :, :-1]
    last_channel = copy.deepcopy(results_image[:, :, 3])
    for channel in range(3):
        segmentation_image[:, :, channel] = last_channel
    for item in range(len(random_items_list)):
        choice_item = random_items_list[item]
        segmentation_image = np.where(segmentation_image == choice_item, color[choice_item], segmentation_image)
    segmentation_image = np.asarray(segmentation_image, dtype=np.uint8)
    segmentation_image = Image.fromarray(segmentation_image[:, :, :3])
    segmentation_image.save(path_of_results.parents[0] / "segmentation" / f"Photo_{name_of_photo}.jpg")


def generate_result_photo(background, scaled_items, path_of_results, name_of_photo, random_items_list):
    result_image, random_spots, crop_spots = overlay_background_with_item(background, scaled_items, random_items_list)
    segmentation_items(result_image, random_items_list, path_of_results, name_of_photo)
    position_of_boxes_to_txt(path_of_results, scaled_items, result_image.shape, random_spots, crop_spots, name_of_photo)
    result_image = Image.fromarray(result_image[:, :, :3])
    result_image.save(path_of_results / f"Photo_{name_of_photo}.jpg")


def generate_photos(items_list, backgrounds_list, path_of_results, items_name_list, results_count, exist_photos):
    name_of_photo = exist_photos
    for no_of_result in range(results_count - exist_photos):
        try:
            name_of_photo += 1
            items, background, random_items_list = load_background_and_item(
                items_list, backgrounds_list, items_name_list, no_of_result
            )
            scaled_items = creating_scaled_item(background, items)
            generate_result_photo(background, scaled_items, path_of_results, name_of_photo, random_items_list)
        except Exception:
            name_of_photo -= 1
            warnings.warn(f"Result photo {name_of_photo} does not create.")


def generate_data(path_of_item, path_of_backgrounds, path_of_data, categories, names_of_items, results_count, delete):
    path_of_data = Path(path_of_data)
    path_of_results = results_to_path(Path(path_of_data), delete)
    exist_photos = len(list(path_of_results.glob("**/*.jpg")))
    items_list, backgrounds_list, items_name_list = list_of_backgrounds_and_items(
        Path(path_of_item), Path(path_of_backgrounds), categories, names_of_items
    )
    generate_photos(items_list, backgrounds_list, path_of_results, items_name_list, results_count, exist_photos)
