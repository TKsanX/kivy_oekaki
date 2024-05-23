from PIL import Image, ImageFilter
import os, tkinter, tkinter.filedialog, tkinter.messagebox
import bz2
import numpy as np
import cv2
import pickle

fTyp = [("", "*")]
iDir = os.path.abspath(os.path.dirname(__file__))
file_name = tkinter.filedialog.askopenfilename(filetypes=fTyp, initialdir=iDir)

print(file_name)
meta = []
Image = Image.open(file_name)
metadata = Image.info
meta = metadata["LineJson"]
meta = pickle.loads(meta)
print(meta)