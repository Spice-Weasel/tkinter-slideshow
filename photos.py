"""
This is a program that will cycle through a directory of
photos and display them on screen.
Change photos_directory to where ever your photos are, no
error handling yet for things that aren't images.
"""

import os, argparse
import pathlib
import datetime as date
from time import sleep
from sys import exit
import tkinter as tk
from PIL import Image, ImageTk, ExifTags

from typing import List
from typing import Tuple
from typing import NewType

from re import split

from screen import Screen

background_colour = "black"

class ImageStore:
    def __init__(self, directory):
        """Setup image store class"""
        self.dir = directory
        self.index = 0

    def __get_paths(self) -> Tuple[List[str], int]:
        """Get names of files in directory"""
        images: List[str]
        images = os.listdir(self.dir)
        return images, len(images)

    def next(self, random: bool = False) -> str:
        """Increment the image counter up to max images
        and return to 0
        TODO: Add random image cycling here"""
        self.image_paths, self.number_of_images = self.__get_paths()
        if self.index >= (self.number_of_images - 1):
            self.index = 0
        else:
            self.index += 1

        return self.image_paths[self.index]

class Application:
    def __init__(self, cycle_period_ms, photos_directory) -> None:
        """Setup the user interface here
        and initialize any dependent classes here
        """
        self.store = ImageStore(photos_directory)
        self.cycle_period_ms = cycle_period_ms

        self.window = tk.Tk()
        self.window.title("Photos")
        self.window.attributes("-fullscreen", True)

        self.display = tk.Label(self.window, bg=background_colour)
        self.display.pack(fill=tk.BOTH)

        self.window.update()

    def increment_image(self) -> None:
        """Get the next image in the directory and
        update the display, call self again in cycle_period_ms"""
        image_path = str(self.store.dir) + '/' + self.store.next()
        print(image_path)
        self.image = self.__open_image(image_path)
        self.__scale_image()
        self.photo_image = ImageTk.PhotoImage(self.image)
        self.display.configure(image = self.photo_image)
        self.window.after(self.cycle_period_ms, self.increment_image)

    def __open_image(self, path : str = None, use_exif_orientation : bool = True) -> Image.Image:
        """Takes a path to an image file and returns a PIL Image object which can be optionally
        rotated in line with exif metadata"""
        if path is None:
            raise ValueError
        image = Image.open(path)
        if use_exif_orientation:
            exif = image.getexif()
            if exif is None:
                pass
            else:
                for key, val in exif.items():
                    if key in ExifTags.TAGS:
                        print(f'{ExifTags.TAGS[key]}:{val}')
                        if  ExifTags.TAGS[key] == 'Orientation':            
                            if val == 3:
                                image=image.transpose(Image.ROTATE_180)
                            elif val == 6:
                                image=image.transpose(Image.ROTATE_270)
                            elif val == 8:
                                image=image.transpose(Image.ROTATE_90)
                            break
        return image

    def __scale_image(self) -> ImageTk:
        """Get the size of the tkinter window - this
        will allow opened images to be scaled accordingly
        """
        window_size_raw = self.window.geometry()
        window_size = split("[x+]", window_size_raw)
        width, height = self.image.size

        print(width, height)

        self.image_scaling_factor = int(window_size[1])/height

        x_size = int(self.image_scaling_factor * width)
        y_size = int(self.image_scaling_factor * height)

        try:
            self.image = self.image.resize((x_size, y_size))
        except ValueError:
            exit(1)



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A simple photo-reel programme")
    parser.add_argument('period_ms', type=int, default=1000)
    parser.add_argument('store', type=pathlib.Path)
    parser.add_argument('on_time', type=int, default=8)
    parser.add_argument('off_time', type=int, default=21)
    parser.add_argument('backlight', type=int, default=0)
    args = parser.parse_args()

    if os.environ.get('DISPLAY','') == '':
        print('no display found. Using :0.0')
        os.environ.__setitem__('DISPLAY', ':0.0')

    app = Application(args.period_ms, args.store)
    app.increment_image()

    if(args.backlight):
        s = Screen()

    while(1):
        try:
            app.window.update()
            app.window.update_idletasks()

            if(args.backlight):    
                time = date.datetime.now()
                if(s.is_on):
                    if(time.hour < args.on_time or time.hour >= args.off_time):
                        s.change_brightness(0)
                        s.is_on = False
                        print("Screen off")
                if(not s.is_on):
                    if(time.hour < args.off_time and time.hour >= args.on_time):
                        s.change_brightness(255)
                        s.is_on = True
                        print("Screen on")

            sleep(1)
            
        except KeyboardInterrupt:
            print("Keyboard interrupt detected, exiting...")
            app.window.destroy()
            break


