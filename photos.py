"""
This is a program that will cycle through a directory of
photos and display them on screen.
Change photos_directory to where ever your photos are, no
error handling yet for things that aren't images.
"""

import os
from time import sleep
from sys import exit
import tkinter as tk
from PIL import Image
from PIL import ImageTk

from typing import List
from typing import Tuple
from typing import NewType

from re import split

photos_directory = '/home/ingram/Pictures/slideshow/'
cycle_period_ms = 1000
background_colour = "black"

class ImageStore:
    def __init__(self, directory):
        """Setup image store class"""
        self.dir = directory
        self.image_paths, self.number_of_images = self.get_paths()
        self.index = 0

    def get_paths(self) -> Tuple[List[str], int]:
        """Get names of files in directory"""
        images: List[str]
        images = os.listdir(self.dir)
        return images, len(images)

    def next(self, random: bool = False) -> str:
        """Increment the image counter up to max images
        and return to 0
        TODO: Add random image cycling here"""
        if self.index >= (self.number_of_images - 1):
            self.index = 0
        else:
            self.index += 1

        return self.image_paths[self.index]

class Application:
    def __init__(self) -> None:
        """Setup the user interface here
        and initialize any dependent classes here
        """
        self.store = ImageStore(photos_directory)

        self.window = tk.Tk()
        self.window.title("Photos")
        self.window.attributes("-fullscreen", True)

        self.display = tk.Label(self.window, bg=background_colour)
        self.display.pack(fill=tk.BOTH)

        self.window.update()

    def increment_image(self) -> None:
        """Get the next image in the directory and
        update the display, call self again in cycle_period_ms"""
        self.image = Image.open(photos_directory + self.store.next())
        self.scale_image()
        self.photo_image = ImageTk.PhotoImage(self.image)
        self.display.configure(image = self.photo_image)
        self.window.after(cycle_period_ms, self.increment_image)

    def scale_image(self) -> ImageTk:
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
    app = Application()
    app.increment_image()
    app.window.mainloop()

