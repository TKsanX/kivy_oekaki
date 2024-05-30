import numpy as np
import cv2
import glob
import os
from PIL import Image, ImageFilter
import os, tkinter, tkinter.filedialog, tkinter.messagebox
import bz2
import numpy as np
import cv2
import pickle

# 8近傍の定義
neiborhood8 = np.array([[1, 1, 1],
                            [1, 1, 1],
                            [1, 1, 1]],
                            np.uint8)

kernel = np.ones((2, 2), np.uint8)

def scale_to_resolation(img, resolation):
    """指定した解像度になるように、アスペクト比を固定して、リサイズする。
    """
    h, w = img.shape[:2]
    scale = (resolation / (w * h)) ** 0.5
    return cv2.resize(img, dsize=None, fx=scale, fy=scale)

fTyp = [("", "*")]
iDir = os.path.abspath(os.path.dirname(__file__))
file_name = tkinter.filedialog.askopenfilename(filetypes=fTyp, initialdir=iDir)


for path in glob.glob(file_name):
    if (os.path.basename(path) == 'Thumbs.db'):
        continue
    img = cv2.imread(path) # 0なしでカラー
    dst = scale_to_resolation(img, 640 * 480)
    img = cv2.cvtColor(dst.astype(np.uint8), cv2.COLOR_RGBA2RGB)
    cv2.floodFill(img,None, (10,10) ,(255,255,255))
    gray = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_RGB2GRAY)
    img_dilate = cv2.dilate(gray, neiborhood8, iterations=1)
    img_diff = cv2.absdiff(gray, img_dilate)
    img_diff_not = cv2.bitwise_not(img_diff)
    at = cv2.adaptiveThreshold(img_diff_not, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 7, 8)

    h,w = at.shape[:2]
    img2 = cv2.resize(at, (w*2, h*2))
    
    r = 1
    for y in range(h):
	    for x in range(w):
		    if img_diff_not[y, x] <= 240:
			    cv2.rectangle(img2,(2*x-r, 2*y-r), (2*x+r, 2*y+r), (0,0,0), -1)
    img2 = cv2.dilate(img2, neiborhood8, iterations=1)
    img3 = cv2.resize(img2, (w, h))
    at = cv2.adaptiveThreshold(img3, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 51, 20)

cv2.imshow('test6',at)

cv2.waitKey()
cv2.destroyAllWindows()
