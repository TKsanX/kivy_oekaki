import cv2
import numpy as np
def image_process(color,gray,cood):

    cood = (int(cood[0]), int(cood[1]))

    height, width = gray.shape[:2]

    center_x, center_y = cood[0], cood[1]  # 画像の中心
    radius = 20  # 円の半径

    # 円形のマスクを作成
    mask = np.zeros((height, width), dtype=np.uint8)
    cv2.circle(mask, (center_x, center_y), radius, 255, -1)

    # マスクを3チャンネルに拡張（カラー画像用）
    mask_3channel = cv2.merge([mask, mask, mask])

    img1_bg = cv2.bitwise_and(gray, 255 - mask_3channel)
    img2_fg = cv2.bitwise_and(color, mask_3channel)
    gray = cv2.add(img1_bg, img2_fg)

    return gray

   