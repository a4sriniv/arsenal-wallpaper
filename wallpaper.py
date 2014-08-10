#!/usr/local/bin/python
"""Script to update a directory with the latest arsenal.com wallpapers.

Usage:
    wallpaper.py --dir <path/to/directory>
"""
import argparse
import os
import wget
import re
import shutil
import logging


class ArsenalWallpaperExtractor(object):
    """Class to extract wallpapers from arsenal.com."""

    def __init__(self, wallpaper_directory):
        self.file = ""
        self.arsenal_wallpapers_link = \
            "http://www.arsenal.com/fanzone/wallpapers"
        self.wallpaper_directory = _check_wallpaper_directory(
            wallpaper_directory)
        self.latest_picture_number = self._get_latest_picture_number()


    def _get_latest_picture_number(self):
        """Gets number of latest picture in user directory.

        Returns: Picture number (string).
        """
        files = os.listdir(self.wallpaper_directory)
        logging.info('Current files in wallpaper directory: ' + str(files))
        picture_numbers = []
        for filename in files:  # TODO: try and make this a list comprehension
            match = re.search(r'gun__(\d+)_3.jpg', filename)
            if match:
                picture_numbers.append(match.group(1))
        if not picture_numbers:
            return "0"  # TODO: Still need to fix bugs for directory with no
            # new pictures
        picture_numbers.sort(reverse=True)
        return str(picture_numbers[0])

    def _download_html_file(self):
        """Downloads arsenal.com wallpaper page."""
        # TODO: check if file already exists
        self.file = wget.download(self.arsenal_wallpapers_link, bar=None)

    def _delete_html_file(self):
        """Deletes local copy of arsenal.com html wallpaper page."""
        os.remove(os.path.join(os.getcwd(), self.file))


    def _parse_html_file(self):
        """Parse arsenal html page for wallpaper links.

        Returns:
            A list of (date,picture number) tuples representing wallpapers
            found.
        """
        with open(self.file, 'r') as html_file:
            file_contents = html_file.read()
        regex = r'/assets/_files/desktops/(\w+_\d+)/gun__(\d+)_3.jpg'
        date_and_number_tuples = _sort_by_picture_number(
            re.findall(regex, file_contents))
        return date_and_number_tuples


    def _get_newer_pictures(self, date_and_number_tuples):
        """Downloads any new pictures from arsenal.com

        This method checks if any wallpapers on the arsenal website are newer
        than the images currently present in the wallpaper directory and
        proceeds to download the pictures.

        Args:
            date_and_number_tuples: Each pair here represents a picture
            present on the arsenal website. The list is assumed to be sorted
            in reverse order by picture number.
        """
        if date_and_number_tuples[0][1] <= self.latest_picture_number:
            print('No new pictures found!')
            return
        picture_count = 0
        for date_and_number_tuple in date_and_number_tuples:
            if date_and_number_tuple[1] > self.latest_picture_number:
                url = 'http://www.arsenal.com/assets/_files/desktops/%s/gun__' \
                      '%s_3.jpg' % (date_and_number_tuple)
                logging.info('Fetching image from url %s', url)
                picture_name = wget.download(url, bar=None)
                logging.info('Copying picture %s to %s ....', picture_name,
                             self.wallpaper_directory)
                if self._not_current_directory():
                    shutil.copy(picture_name, self.wallpaper_directory)
                    os.remove(os.path.join(os.getcwd(), picture_name))
                picture_count += 1
            else:
                break
        print('%d pictures downloaded!' % picture_count)

    def _not_current_directory(self):
        """Checks to see if user directory is the current directory."""
        return os.getcwd() != self.wallpaper_directory

    def extract_wallpapers(self):
        """Extracts wallpapers from arsenal.com and downloads them to the user
        directory."""
        self._download_html_file()
        self._get_newer_pictures(self._parse_html_file())
        self._delete_html_file()


def _check_wallpaper_directory(wallpaper_dir):
    """Checks if wallpaper_dir exists and creates dir if necessary.

    Args:
        wallpaper_dir: Directory to check/create.
    Returns:
        Absolute directory path.
    """
    directory = os.path.abspath(wallpaper_dir)
    if not os.path.isdir(directory):
        os.makedirs(directory)
    return directory


def _sort_by_picture_number(date_and_number_tuples):
    """Sorts (date, number) tuples by the number field in reverse order.

    Args:
        date_and_number_tuples: List of tuples.
    Returns:
        Sorted list.
    """
    return sorted(date_and_number_tuples, key=lambda pair: int(pair[1]),
                  reverse=True)


def get_new_wallpapers(directory):
    """Update directory with any new wallpapers from arsenal.com."""
    extractor = ArsenalWallpaperExtractor(directory)
    extractor.extract_wallpapers()


def main():
    args = parser.parse_args()
    print('Extracting wallpapers from arsenal.com .....')
    get_new_wallpapers(args.dir)

# set logging level and log file
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='wallpaper.log', level=logging.DEBUG)

# parse command line arguments
parser = argparse.ArgumentParser(
    description='Tool to obtain new arsenal.com wallpapers')
parser.add_argument('-d', '--dir', required=True,
                    help='Directory in which wallpapers will be downloaded to.')

if __name__ == "__main__":
    main()
