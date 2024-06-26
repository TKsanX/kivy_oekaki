import cv2


# 画像の読み込み
img = cv2.imread('./nurie/komuyuki.png')
# 2値化

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
#白と黒を反転
binary = cv2.bitwise_not(binary)
# が慈雨の保存
cv2.imwrite('./nurie/komuyuki_binary.png', binary)