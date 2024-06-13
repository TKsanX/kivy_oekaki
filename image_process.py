import cv2
import numpy as np



def image_process(color,gray,cood,cood_hist,Window,line_width):

    cood = (int(cood[0]), int(cood[1]))


    # 円形のマスクを作成
    mask = np.zeros((Window.height, Window.width), dtype=np.uint8)

    cv2.line(mask, cood, cood_hist, 255, line_width)

    # マスクを3チャンネルに拡張（カラー画像用）
    mask_3channel = cv2.merge([mask, mask, mask])


    img1_bg = cv2.bitwise_and(gray, 255 - mask_3channel)
    img2_fg = cv2.bitwise_and(color, mask_3channel)
    gray = cv2.add(img1_bg, img2_fg)

    cv2.imwrite('test7.png', mask_3channel)

    cood_hist = (int(cood[0]), int(cood[1]))

    return gray,cood_hist

   