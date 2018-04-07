import numpy as np

import math

import matplotlib.pyplot
import socket

from PIL import Image, ImageFont, ImageFilter, ImageDraw

from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier


class AsciiImageProcessing:
    
    def __init__(self, font_size,
                 list_of_symbols: list = list(set('SDFGHJKL:;.,QWE1290!@#$%^&*_+-=`~?(){}[]|\\|/')),
                 default_size=(640, 480)):
        
        self._generate_font_array(font_size, list_of_symbols)
        self.default_size = default_size
        self.list_of_symbols = list_of_symbols[:]
    
    def _generate_font_array(self,
                             font_size: int,
                             list_of_symbols: list):
        height = int(font_size * 1.2)
        width = int(font_size / 1.65)
        self.he = height
        self.wi = width
        
        font = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf', font_size)
        
        self.patterns = []
        
        for current_symbol in list_of_symbols:
            pattern_image = Image.new('F', (width, height), color=1)
            pattern_drawer = ImageDraw.Draw(pattern_image)
            
            pattern_drawer.text((0, 0), text=current_symbol, font=font, fill=0)
            
            self.patterns.append(np.array(pattern_image).ravel())
        
        self.patterns = np.array(self.patterns)
        
        self.classifier = KNeighborsClassifier(n_neighbors=1)
        self.classifier.fit(self.patterns, list(range(len(list_of_symbols))))
    
    def load_image(self, image_file):
        image = Image.open(image_file)
        
        width = image.size[0]
        height = image.size[1]
        
        new_width = self.default_size[0]
        new_height = int(height * new_width / width)
        
        image = image.resize((new_width, new_height))
        
        return image
    
    @staticmethod
    def transform_image(im: Image):
        image = im
        try:
    
            width = image.size[0]
            height = image.size[1]
    
            image = image.filter(ImageFilter.SHARPEN)
    
            image2 = image.filter(ImageFilter.CONTOUR)
            image2 = image2.filter(ImageFilter.MinFilter(3)).convert('L').filter(ImageFilter.MedianFilter(3))
            image = image.convert('L')
    
            image2.save('images/tmp.png')
            image = np.array(image)
            image2 = np.array(image2)
    
            image_transformed = np.zeros((height, width))
            image2_transformed = np.zeros((height, width))
    
            for i in range(height):
                for j in range(width):
                    image_transformed[i, j] = (image[i, j] / 256 - 1 / 3) / 2 + 1 / 3
                    image2_transformed[i, j] = image2[i, j] / 256
    
            image_transformed = 1 - (1 - image_transformed) / 3 + image2_transformed * 2
            image_transformed = image_transformed - np.min(image_transformed)
            image_transformed /= np.max(image_transformed)
    
            image_transformed = (image_transformed - 0.2) / 1.3 + 0.1
    
            return image_transformed
        
        except Exception as e:
            print(e)
    
    def resize_image(self, image: np.ndarray):
        
        vertical_addition = self.he - image.shape[0] % self.he
        up_addition = vertical_addition // 2
        down_addition = vertical_addition - up_addition
        horizontal_addition = self.wi - image.shape[1] % self.wi
        left_addition = horizontal_addition // 2
        right_addition = horizontal_addition - left_addition
        
        # print(image.shape)
        
        # print(left_addition, right_addition, horizontal_addition)
        # print(up_addition, down_addition, vertical_addition)
        
        left_addition = np.zeros((image.shape[0], left_addition))
        right_addition = np.zeros((image.shape[0], right_addition))
        
        image = np.append(left_addition, image, axis=1)
        image = np.append(image, right_addition, axis=1)
        
        up_addition = np.zeros((up_addition, image.shape[1]))
        down_addition = np.zeros((down_addition, image.shape[1]))
        
        image = np.append(up_addition, image, axis=0)
        image = np.append(image, down_addition, axis=0)
        
        return image
    
    def image_to_text(self, image: np.ndarray):
        batch = []
        result = ''
        
        for x in range(0, image.shape[0], self.he):
            for y in range(0, image.shape[1], self.wi):
                batch.append(image[x: x + self.he, y: y + self.wi].ravel())
        
        q = self.classifier.predict(batch)
        sd = 0
        for x in range(0, image.shape[0], self.he):
            for y in range(0, image.shape[1], self.wi):
                result = result + self.list_of_symbols[q[sd]]
                sd += 1
            result += '\n'
        
        return result
    
    @staticmethod
    def upload_ascii(text):
        
        sock = socket.create_connection(("tcpst.net", 7777))
        sock.sendall(text.encode())
        sock.settimeout(1)
        reply = b""
        while True:
            try:
                reply += sock.recv(4096)
            except:
                break
        url = {key: value for key, value in [line.split(b" ") for line in reply.split(b"\n") if line]}[b"URL"]
        return url.decode('utf-8')
    
    def Process(self, filename):
        
        s = self.load_image(filename)
        s = self.transform_image(s)
        s = self.resize_image(s)
        s = self.image_to_text(s)
        return s
