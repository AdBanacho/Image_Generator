import imghdr
import os
import posixpath
import re
import shutil
import urllib
import urllib.request


class Bing:
    def __init__(self, query, exist_count, limit, output_dir, adult, timeout, filters=""):
        self.download_count = 0
        self.query = query
        self.output_dir = output_dir
        self.adult = adult
        self.filters = filters
        self.exist_count = exist_count

        assert type(limit) == int, "limit must be integer"
        self.limit = limit
        assert type(timeout) == int, "timeout must be integer"
        self.timeout = timeout

        self.headers = {"User-Agent": "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0"}
        self.page_counter = 0

    def save_image(self, link, file_path):
        request = urllib.request.Request(link, None, self.headers)
        image = urllib.request.urlopen(request, timeout=self.timeout).read()
        if not imghdr.what(None, image):
            raise
        with open(file_path, "wb") as f:
            f.write(image)

    def download_image(self, link):
        self.download_count += 1

        # Get the image link
        try:
            path = urllib.parse.urlsplit(link).path
            filename = posixpath.basename(path).split("?")[0]
            file_type = filename.split(".")[-1]
            if file_type.lower() not in ["jpg", "png"]:
                file_type = "jpg"

            self.save_image(
                link,
                "{}/{}/".format(self.output_dir, self.query)
                + "Background_{}.{}".format(str(self.exist_count + self.download_count), file_type),
            )
        except Exception:
            self.download_count -= 1

    def run(self):
        while self.download_count < self.limit:
            # Parse the page source and download pics
            request_url = (
                "https://www.bing.com/images/async?q="
                + urllib.parse.quote_plus(self.query)
                + "&first="
                + str(self.page_counter)
                + "&count="
                + str(self.limit)
                + "&adlt="
                + self.adult
                + "&qft="
                + self.filters
            )
            request = urllib.request.Request(request_url, None, headers=self.headers)
            response = urllib.request.urlopen(request)
            html = response.read().decode("utf8")
            links = re.findall("murl&quot;:&quot;(.*?)&quot;", html)

            for link in links:
                if self.download_count < self.limit:
                    self.download_image(link)
                else:
                    break

            self.page_counter += 1


def download(
    query, exist_count=0, limit=100, output_dir="backgrounds", adult_filter_off=True, force_replace=False, timeout=60
):
    # engine = 'bing'
    if adult_filter_off:
        adult = "off"
    else:
        adult = "on"

    image_dir = os.path.join(output_dir, query)

    if force_replace and os.path.isdir(image_dir):
        shutil.rmtree(image_dir)

    if not os.path.isdir("{}/".format(output_dir)):
        os.makedirs("{}/".format(output_dir))

    if not os.path.isdir("{}/{}".format(output_dir, query)):
        os.makedirs("{}/{}".format(output_dir, query))

    bing = Bing(query, exist_count, limit, output_dir, adult, timeout)
    bing.run()
