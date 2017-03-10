#!/usr/bin/env python
import cStringIO
from PIL import Image
from app.utils import Singleton

class Compression(object):
    __metaclass__ = Singleton

    __MAXSIZE = 1440, 1080

    def compress(self, file):
        im = Image.open(file)
        im.thumbnail(self.__MAXSIZE, Image.ANTIALIAS)
        compressedImg = cStringIO.StringIO()
        im.save(compressedImg, 'JPEG', quality=75)
        return compressedImg.getvalue()
