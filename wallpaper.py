import os
import wget
import re
import shutil
import logging

class ArsenalWallpaperExtractor(object):
    
    def __init__(self):
        self.file = ""
        self.arsenal_wallpapers_link = "http://www.arsenal.com/fanzone/wallpapers"
        self.wallpaper_directory = "/Users/Adithya/Desktop/Stuff/Arsenal/2014-15" # TODO: should parameterize
        self.latest_picture_number = self._get_latest_picture_number()

    def _get_latest_picture_number(self):
        files = os.listdir(self.wallpaper_directory)
        logging.info('Current wallpaper files: ' + str(files))
        picture_numbers = []
        for filename in files: # TODO: try and make this a list comprehension
            m = re.search(r'gun__(\d+)_3.jpg', filename)
            if m:
                picture_numbers.append(m.group(1))
        picture_numbers.sort(reverse=True)
        return picture_numbers[0]

    def download_html_file(self):
        # TODO: check if file already exists
        self.file = wget.download(self.arsenal_wallpapers_link, bar=None)

    def delete_html_file(self):
        os.remove(os.path.join(os.getcwd(), self.file))

    def parse_html_file(self):
        with open(self.file, 'r') as f:
            file_contents = f.read()
        regex = '/assets/_files/desktops/\w+_\d+/gun__(\d+)_3.jpg'
        picture_numbers = re.findall(regex, file_contents)
        picture_numbers.sort(reverse=True)
        return picture_numbers

    def get_newer_pictures(self, picture_numbers):
        if picture_numbers[0] <= self.latest_picture_number:
            print('No new pictures found!')
            return
        picture_count = 0
        for picture_number in picture_numbers:
            if picture_number > self.latest_picture_number:
                picture_name = wget.download('http://www.arsenal.com/assets/_files/desktops/jul_14/gun__%s_3.jpg' % picture_number, bar=None)
                logging.info('Copying picture %s to %s ....', picture_name, self.wallpaper_directory)
                shutil.copy(picture_name, self.wallpaper_directory)
                os.remove(os.path.join(os.getcwd(), picture_name))
                picture_count += 1
            else:
                break
        print('%d pictures downloaded!' % picture_count)

    def extract_wallpapers(self):
        self.download_html_file()
        self.get_newer_pictures(self.parse_html_file())
        self.delete_html_file()

def get_new_wallpapers():
    extractor = ArsenalWallpaperExtractor()
    extractor.extract_wallpapers()

def main():
    print 'Extracting wallpapers from arsenal.com .....' 
    get_new_wallpapers()

# set logging level and log file
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', filename='wallpaper.log', level=logging.DEBUG)

if __name__ == "__main__":
    main()
