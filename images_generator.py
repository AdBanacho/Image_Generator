import shutil
import warnings

from pathlib import Path

import numpy as np

from PIL import Image

from images_transformation import brightness, cut_blank_place, transformations_of_images


def transforming_items(batch_size, item, path_of_config):
    items_to_transforming = np.zeros((batch_size, *item.shape[:3]))
    for item_in_batch in range(batch_size):
        items_to_transforming[item_in_batch] = item
    items_to_transforming = brightness(items_to_transforming, path_of_config)
    items_to_transforming = items_to_transforming.astype(np.uint8)
    sequence_of_transforms = transformations_of_images(path_of_config)
    return sequence_of_transforms(images=items_to_transforming)


def creating_new_items(path_of_names, item, items_count, name_of_item, path_of_config):
    exist = list(path_of_names.glob("**/*.png"))
    batch_size = 100
    batches_count = (items_count - len(exist)) // batch_size + 1
    no_of_item_name = len(exist) // batch_size
    for batch_count in range(batches_count):
        if batch_count == batches_count - 1:
            batch_size = items_count % batch_size
        try:
            items_transformed = transforming_items(batch_size, item, path_of_config)
            no_of_item_name += 1
            for item_in_batch in range(batch_size):
                try:
                    items_transformed[item_in_batch] = cut_blank_place(items_transformed[item_in_batch])
                    transformed_item = Image.fromarray(items_transformed[item_in_batch])
                    transformed_item.save(path_of_names / f"{name_of_item}_{no_of_item_name}_{item_in_batch + 1}.png")
                except Exception:
                    warnings.warn(
                        f"Name of item {name_of_item}. In {batch_count + 1} item {item_in_batch} does not create"
                    )
        except Exception:
            warnings.warn(
                f"Name of item {name_of_item}. Batch {batch_count + 1} does not create. Batch size {batch_size}"
            )


def generate_items(uploaded_files, path_of_item, items_count, names_of_items, delete, path_of_config):
    path_of_item = Path(path_of_item)
    for no_of_item in range(len(names_of_items)):
        path_of_named_item = path_of_item / names_of_items[no_of_item]
        if not path_of_item.is_dir():
            path_of_item.mkdir()
        if not path_of_named_item.is_dir():
            path_of_named_item.mkdir()
        else:
            if delete:
                shutil.rmtree(path_of_named_item)
                path_of_named_item.mkdir()
        while len(list(path_of_named_item.glob("**/*.png"))) != items_count:
            creating_new_items(
                path_of_named_item, uploaded_files[no_of_item], items_count, names_of_items[no_of_item], path_of_config
            )
