from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Rectangle, Color, Line
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.core.window import Window
import cv2
from kivy.core.image import Image as CoreImage


class BackgroundLayer(Widget):
    def __init__(self, **kwargs):
        super(BackgroundLayer, self).__init__(**kwargs)

        raw_img = "sp1.png"
        top_img = "test6.png"
        file = cv2.imread(raw_img, cv2.IMREAD_UNCHANGED)
        file2 = cv2.imread(top_img, cv2.IMREAD_UNCHANGED)

        c_width = int(Window.width)
        c_height = int(Window.height)
        
        print("c_width:" + str(c_width))
        print("c_height:" + str(c_height))
        
        try:
            print(str(file.shape[0])) # 縦
            print(str(file.shape[1])) # 横
        except:
            return
        mag_height = c_height / file.shape[0]
        mag_width = c_width / file.shape[1]
        
        if mag_height < mag_width:
            mag = mag_height
        else:
            mag = mag_width
        c_width = int(file.shape[1] * mag)
            
        
        res_img1 = cv2.resize(file, dsize = (c_width, c_height))
        res_img2 = cv2.resize(file2, dsize = (c_width, c_height))


        cv2.imwrite('nurie.png', res_img1)
        
        cv_image1 = CoreImage.load("./nurie.png")
        cv_image1 = cv_image1.texture


        cv2.imwrite('nurie2.png', res_img2)
        
        cv_image2 = CoreImage.load("./nurie2.png")
        cv_image2 = cv_image2.texture

        # 背景レイヤー
        with self.canvas:
            Color(1, 1, 1, 1)  # 緑色
            Rectangle(texture=cv_image1, pos=(0, 0), size=(c_width, c_height))



class FrontLayer(Widget):
    def __init__(self, **kwargs):
        super(FrontLayer, self).__init__(**kwargs)
        self.stroke = []    
        raw_img = "sp1.png"
        top_img = "test6.png"
        file = cv2.imread(raw_img, cv2.IMREAD_UNCHANGED)
        file2 = cv2.imread(top_img, cv2.IMREAD_UNCHANGED)

        c_width = int(Window.width)
        c_height = int(Window.height)
        
        print("c_width:" + str(c_width))
        print("c_height:" + str(c_height))
        
        try:
            print(str(file.shape[0])) # 縦
            print(str(file.shape[1])) # 横
        except:
            return
        mag_height = c_height / file.shape[0]
        mag_width = c_width / file.shape[1]
        
        if mag_height < mag_width:
            mag = mag_height
        else:
            mag = mag_width
        c_width = int(file.shape[1] * mag)
            
        
        res_img1 = cv2.resize(file, dsize = (c_width, c_height))
        res_img2 = cv2.resize(file2, dsize = (c_width, c_height))


        cv2.imwrite('nurie.png', res_img1)
        
        cv_image1 = CoreImage.load("./nurie.png")
        cv_image1 = cv_image1.texture
    

        cv2.imwrite('nurie2.png', res_img2)
        
        cv_image2 = CoreImage.load("./nurie2.png")
        cv_image2 = cv_image2.texture


        # 背景レイヤー
        with self.canvas:
            Color(1, 1, 1, 1)  # 緑色

    def on_touch_down(self, touch):
        
        with self.canvas:
            Color(rgba=(1, 1, 1, 1))
            touch.ud['line'] = Line(points=(touch.x, touch.y), width=12, rgba=(1, 1, 1, 0))
        self.drawing = True

    def on_touch_move(self, touch):
        print(touch.x)
        if self.drawing:
            touch.ud["line"].points += [touch.x, touch.y]

    def on_touch_up(self, touch):

        if self.drawing:
            self.drawing = False
            self.stroke.append(touch.ud['line'])

class LayeredApp(App):
    def build(self):
        layout = FloatLayout()
        layout.add_widget(BackgroundLayer())
        
        self.front_layer = FrontLayer()
        layout.add_widget(self.front_layer)

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        return layout

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == '1':
            self.middle_layer.canvas.clear()  # 中間レイヤーをクリア
        elif keycode[1] == '2':
            self.front_layer.canvas.clear()  # 前景レイヤーをクリア
        return True

if __name__ == '__main__':
    LayeredApp().run()