#!/usr/bin/env python
import cStringIO
from PIL import Image
from app.utils import Singleton

class Compression(object):
    __metaclass__ = Singleton

    __MAXSIZE = 1440, 1440

    def compress(self, file):
        im = Image.open(file)
        im.thumbnail(self.__MAXSIZE, Image.ANTIALIAS)
        newIm = cStringIO.StringIO()
        im.save(newIm, 'JPEG')
        return newIm.getvalue()
