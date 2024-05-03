from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
from collections import deque

def fill_region(image, seed_point, fill_color):
    q = [seed_point]  # 探索待ちキュー
    region = []       # 塗りつぶし領域の座標リスト
    while q:
        x, y = q.pop(0)  # キューから座標を取り出す
        if image[y][x] != fill_color:  # その座標の色が塗りつぶし色と異なれば
            region.append((x, y))      # 領域リストに追加し
            image[y][x] = fill_color   # その座標を塗りつぶし色に変える
            # その座標の上下左右の未探索座標をキューに追加
            for dx, dy in (0, 1), (0, -1), (1, 0), (-1, 0):
                x2, y2 = x + dx, y + dy
                if (0 <= x2 < width) and (0 <= y2 < height):
                    q.append((x2, y2))
    return region