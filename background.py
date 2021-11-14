import shutil

from pathlib import Path

from bing_downloader_images import download


def download_backgrounds_from_bing(categories, backgrounds_count, exist_backgrounds, path_of_backgrounds):
    for no_of_category, category in enumerate(categories):
        download(
            category,
            exist_count=exist_backgrounds[no_of_category],
            limit=backgrounds_count - exist_backgrounds[no_of_category],
            output_dir=path_of_backgrounds,
            adult_filter_off=True,
            force_replace=False,
            timeout=60,
        )


def generate_backgrounds(categories, backgrounds_count, path_of_backgrounds, delete):
    path_of_backgrounds = Path(path_of_backgrounds)
    if delete and path_of_backgrounds.isdir():
        shutil.rmtree(path_of_backgrounds)
    exist_backgrounds = []
    for category in range(len(categories)):
        path_of_categories = path_of_backgrounds / categories[category]
        exist = list(path_of_categories.glob("**/*.*g"))
        exist_backgrounds.append(len(exist))
    download_backgrounds_from_bing(categories, backgrounds_count, exist_backgrounds, path_of_backgrounds)
