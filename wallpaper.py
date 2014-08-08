#!/usr/local/bin/python

import argparse
import os
import wget
import re
import shutil
import logging

class ArsenalWallpaperExtractor(object):
    
    def __init__(self):
        self.file = ""
        self.arsenal_wallpapers_link = "http://www.arsenal.com/fanzone/wallpapers"
        self.wallpaper_directory = self._get_wallpaper_directory()
        self.latest_picture_number = self._get_latest_picture_number()

    def _get_wallpaper_directory(self):
        directory = os.path.abspath(args.dir)
        if not os.path.isdir(directory):
            os.makedirs(directory)
        return directory

    def _get_latest_picture_number(self):
        files = os.listdir(self.wallpaper_directory)
        logging.info('Current files in wallpaper directory: ' + str(files))
        picture_numbers = []
        for filename in files: # TODO: try and make this a list comprehension
            m = re.search(r'gun__(\d+)_3.jpg', filename)
            if m:
                picture_numbers.append(m.group(1))
        if not picture_numbers:
            return 0 # TODO: Still need to fix bugs for directory with no new pictures
        picture_numbers.sort(reverse=True)
        return picture_numbers[0]

    def _download_html_file(self):
        # TODO: check if file already exists
        self.file = wget.download(self.arsenal_wallpapers_link, bar=None)

    def _delete_html_file(self):
        os.remove(os.path.join(os.getcwd(), self.file))

    def _sort_by_picture_number(self, date_and_number_tuples):
        return sorted(date_and_number_tuples, key=lambda pair: pair[1], reverse=True)
    
    def _parse_html_file(self):
        with open(self.file, 'r') as f:
            file_contents = f.read()
        regex = '/assets/_files/desktops/(\w+_\d+)/gun__(\d+)_3.jpg'
        date_and_number_tuples = self._sort_by_picture_number(re.findall(regex, file_contents))
        return date_and_number_tuples


    def _get_newer_pictures(self, date_and_number_tuples):
        if date_and_number_tuples[0][1] <= self.latest_picture_number:
            print('No new pictures found!')
            return
        picture_count = 0
        for date_and_number_tuple in date_and_number_tuples:
            if date_and_number_tuple[1] > self.latest_picture_number:
                url = 'http://www.arsenal.com/assets/_files/desktops/%s/gun__%s_3.jpg' % (date_and_number_tuple)
                logging.info('Fetching image from url %s', url)
                picture_name = wget.download(url, bar=None)
                logging.info('Copying picture %s to %s ....', picture_name, self.wallpaper_directory)
                if self._not_current_directory():
                    shutil.copy(picture_name, self.wallpaper_directory)
                    os.remove(os.path.join(os.getcwd(), picture_name))
                picture_count += 1
            else:
                break
        print('%d pictures downloaded!' % picture_count)

    def _not_current_directory(self):
        return os.getcwd() != self.wallpaper_directory

    def _extract_wallpapers(self):
        self._download_html_file()
        self._get_newer_pictures(self._parse_html_file())
        self._delete_html_file()

def get_new_wallpapers():
    extractor = ArsenalWallpaperExtractor()
    extractor._extract_wallpapers()

def main():
    print 'Extracting wallpapers from arsenal.com .....' 
    get_new_wallpapers()

# set logging level and log file
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', filename='wallpaper.log', level=logging.DEBUG)

# parse command line arguments
parser = argparse.ArgumentParser(description='Tool to obtain new arsenal.com wallpapers')
parser.add_argument('-d', '--dir',  required=True, help='Directory in which wallpapers will be downloaded to.')
args = parser.parse_args()

if __name__ == "__main__":
    main()
