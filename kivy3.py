from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle

class TriangleDrawer(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(on_touch_down=self.on_touch)

    def on_touch(self, instance, touch):
        if touch.is_double_tap:
            return
        
        # クリック位置を取得
        touch_x, touch_y = touch.pos
        
        # 三角形の頂点を計算
        size = 50  # 三角形のサイズ
        p1 = (touch_x, touch_y)
        p2 = (touch_x + size, touch_y)
        p3 = (touch_x + size/2, touch_y + size * 0.866)
        
        with self.canvas:
            # 三角形を描画
            Color(1, 0, 0)  # 赤色
            Rectangle(pos=p1, size=(1, 1))  # 頂点1
            Rectangle(pos=p2, size=(1, 1))  # 頂点2
            Rectangle(pos=p3, size=(1, 1))  # 頂点3

class TriangleApp(App):
    def build(self):
        return TriangleDrawer()

if __name__ == '__main__':
    TriangleApp().run()