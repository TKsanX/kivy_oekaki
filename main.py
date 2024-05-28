from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.screenmanager import ScreenManager #, Screen
from kivy.uix.screenmanager import FadeTransition
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText
from kivy.clock import Clock
from kivymd.uix.navigationrail import MDNavigationRailItem
from kivy.uix.pagelayout import PageLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivy.uix.image import Image as KvImage
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics.texture import Texture
from kivy.core.image import Image as CoreImage
import os, tkinter, tkinter.filedialog, tkinter.messagebox
import pickle
import bz2

from copy import deepcopy



import kivymd.icon_definitions

import gc
import cv2
import numpy as np
import math
import json
import time
import os

from PIL import Image
from PIL.PngImagePlugin import PngInfo

color_picker = (0, 0, 0, 1)
gl_save_count = 0

#! デバッグ用モード切替
#! 0:塗りつぶしモード
#! 1:描画モード
write_mode = 0



# Declare both screens
class MenuScreen(MDScreen):
    pass

class PainterScreen(MDScreen):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.color_picker = (0, 0, 0, 1)
        self.drawing = False
        self.stroke = []
        self.undo_strokes = []
        self.color_history = []
        self.save_count = 0
        self.image_history = [] 
        self.load_state = False
        self.final_shape = []
        

    def on_image1_down(self, touch):
        if write_mode == 0:
            if self.collide_point(*touch.pos):
                self.fill(touch)
        else:
            if self.collide_point(*touch.pos):
                with self.canvas:
                    Color(rgba=self.color_picker)
                    self.color_history.append(self.color_picker)
                    touch.ud['line'] = Line(points=(touch.x, touch.y), width=2, rgba=(0, 0, 0, 0))
                self.drawing = True

    def fill(self, touch):
        global gl_save_count
        global countA
        global cv_image
        x = touch.x
        y = touch.y

        width_canvas = self.ids.main_canvas.width 
        hight_root = self.height

        print(width_canvas)
        if self.final_shape == [str(width_canvas), str(hight_root)]:
            

            bgr_array = deepcopy(self.image_history[-1])
            
            print(len(bgr_array))
            bgr_array = cv2.flip(bgr_array, 0, bgr_array)
            print("履歴読み込み")
        else:
            self.export_to_png('temp.png')

            raw_image = Image.open('temp.png')
            cuted_image = raw_image.crop((0, 0, width_canvas, hight_root))

            cv2.imwrite('temp.png', np.array(cuted_image))

            bgr_array = cv2.imread('temp.png')
            bgr_array = cv2.cvtColor(bgr_array, cv2.COLOR_BGR2RGB)
            print("新規読み込み")

        print(self.final_shape)
        print([width_canvas, hight_root])

        image_shape = bgr_array.shape
        fix_y = abs(int(y) - image_shape[0])
        
        
        color_picker_255 = tuple(component * 255 for component in self.color_picker[:3])
        color_picker_255 = color_picker_255[::-1]
        print(color_picker_255)

        color_value = bgr_array[int(fix_y), int(x)]
        
        cv2.floodFill(bgr_array,None , (int(x), int(fix_y)), color_picker_255)

        cv2.flip(bgr_array, 0, bgr_array)
        
        self.image_history.append(bgr_array)
        self.final_shape = [str(width_canvas), str(hight_root)]


        texture_canvas = Texture.create(size=(image_shape[1], image_shape[0]), colorfmt='bgr')
        texture_canvas.blit_buffer(bgr_array.tobytes(), colorfmt='bgr')
        try:
            cv2.imwrite('temp5.png', self.image_history[2])
        except:
            pass

        with self.canvas:
            touch.ud['image'] = Rectangle(texture=texture_canvas, pos=(0, 0), size=(image_shape[1], image_shape[0]))
        self.drawing = True
        print("img_hist:" + str(len(self.image_history)))
        bgr_array = None
        del bgr_array
        gc.collect()


    def on_image1_move(self, touch):
        if write_mode == 0:
            pass
        else:
            if self.drawing:
                touch.ud["line"].points += [touch.x, touch.y]

    def on_image1_up(self, touch):
        if write_mode == 0:
            if self.drawing:
                self.drawing = False
                self.stroke.append(touch.ud['image'])
            #print(self.image_history)
        else:
            if self.drawing:
                self.drawing = False
                self.stroke.append(touch.ud['line'])

    #* 一つ戻す処理
    def canvas_undo(self):
        if self.stroke:
            stroke = self.stroke.pop()
            self.image_history.pop()
            self.undo_strokes.append(stroke)
            self.canvas.remove(stroke)



    def save_canvas_data(self):
        if write_mode == 0:
            canvas_data = []
            count = 0
            for i in self.image_history:                
                canvas_data.append(self.image_history[count])
                count += 1

            print(canvas_data)
            return canvas_data
        else:
            canvas_data = []
            count = 0
            for stroke in self.stroke:
                color = self.color_history[count]
                count += 1
                points = [round(p, 2) for p in stroke.points]
                width = round(stroke.width, 2)
                canvas_data.append({'points': points, 'width': width, 'color': color})
            print(canvas_data)
            return canvas_data

    def load_canvas_data(self, canvas_data):
        for stroke in self.stroke:
            self.canvas.remove(stroke)
        #キャンバスの色を白にする
        
        self.color_history = []
        self.stroke = []
        with self.canvas:
            for stroke_data in canvas_data:
                Color(rgba=stroke_data['color'])
                line = Line(points=stroke_data['points'], width=stroke_data['width'])
                self.stroke.append(line)
                self.color_history.append(stroke_data['color'])
    
    def color_change_black(self):
        self.color_picker = (0, 0, 0, 1)
    def color_change_red(self):
        self.color_picker = (1, 0, 0, 1)
    def color_change_green(self):
        self.color_picker = (0, 1, 0, 1)
    def color_change_blue(self):
        self.color_picker = (0, 0, 1, 1)
        
    def test_code(self):
        pass

    def load_canvas(self):
        try:
            iDir = os.path.abspath(os.path.dirname(__file__))
            raw_img = tkinter.filedialog.askopenfilename(filetypes=[('Image Files', '*.png')],initialdir=iDir)
            raw_pickle = raw_img.replace('.png', '.pickle')
            for stroke in self.stroke:
                try:
                    self.canvas.remove(stroke)
                except:
                    pass
                #キャンバスの色を白にする
                self.color_history = []
                self.stroke = []
            save_img = Image.open(raw_img)
            width_canvas = self.ids.main_canvas.width 
            hight_root = self.height
            metadata = save_img.info
            meta = []
            height = metadata["height"]
            width = metadata["width"]
            canvas_count = int(metadata["count"])
            
            #! 画像のサイズが異なる場合は読み込まない  
            if int(float(hight_root)) != int(float(height)) and int(float(width_canvas)) != int(float(width)):
                return
            else:
                pass
            
            f = open(raw_pickle, 'rb')
            canvas_array = pickle.load(f)
            f.close()
            
            canvas_array = pickle.loads(canvas_array)

            self.stroke = []
            self.undo_strokes = []
            self.color_history = []
            self.save_count = 0
            self.image_history = [] 
            self.final_shape = [width , height]

            
            
            tmp_count = 0
            
            for i in range(canvas_count):
                texture_canvas = Texture.create(size=(canvas_array[0].shape[1], canvas_array[0].shape[0]), colorfmt='bgr')
                texture_canvas.blit_buffer(canvas_array[i].tobytes(), colorfmt='bgr')

                
                with self.canvas:
                    tmp_rect =  Rectangle(texture=texture_canvas, pos=(0, 0), size=(canvas_array[0].shape[1], canvas_array[0].shape[0])) 
                    if tmp_count != 0:
                        self.stroke.append(tmp_rect)
                    else:
                        if self.load_state == True:
                            self.stroke.append(tmp_rect)
                if tmp_count != 0:
                    self.image_history.append(canvas_array[i])
                else:
                    if self.load_state == True:
                        self.image_history.append(canvas_array[i])
                tmp_count += 1

        except FileNotFoundError:
            print('FileNotFoundError')
    
    def save_image_canvas(self):
        now_time = time.strftime('%Y%m%d%H%M%S', time.localtime())
        fl_name = './saves/image_' + now_time + '.png'
        pi_name = './saves/image_' + now_time + '.pickle'
        
        width_canvas = self.ids.main_canvas.width 
        hight_root = self.height
        self.export_to_png(fl_name)
        raw_image = Image.open(fl_name)
        cutted_image = raw_image.crop((0, 0, width_canvas, hight_root))
        color_rb = cv2.cvtColor(np.array(cutted_image).astype(np.uint8), cv2.COLOR_BGR2RGB)
        
        cv2.imwrite(fl_name, np.array(color_rb))
        
        tmp_image = Image.open(fl_name)

        metadata = PngInfo()
        metadata.add_text('data', now_time)
        canvas_data , canvas_count = self.save_canvas_data()
        metadata.add_text('height', str(hight_root))
        metadata.add_text('width', str(width_canvas))
        metadata.add_text('count', str(canvas_count))
        
        f = open(pi_name, 'wb')
        pickle.dump(canvas_data, f)
        f.close()

        
        tmp_image.save(fl_name, pnginfo=metadata)

    def save_canvas_data(self):
        if write_mode == 0:
            canvas_data = []
            count = 0
            for i in self.image_history:
                images= self.image_history[count]
                canvas_data.append(images)
                count += 1
            print(count)

            canvas_data = pickle.dumps(canvas_data)
            
            return canvas_data , count
        else:
            canvas_data = []
            count = 0
            for stroke in self.stroke:
                color = self.color_history[count]
                count += 1
                points = [round(p, 2) for p in stroke.points]
                width = round(stroke.width, 2)
                canvas_data.append({'points': points, 'width': width, 'color': color})
            print(canvas_data)
            return canvas_data
        
    def load_nurie_data(self):
        iDir = os.path.abspath(os.path.dirname(__file__))
        raw_img = tkinter.filedialog.askopenfilename(filetypes=[('Image Files', '*.png;*.jpg;*.jpeg')],initialdir=iDir)
        
        file = cv2.imread(raw_img, 0)

        threshold = 200
        
        c_width = int(self.ids.main_canvas.width)
        c_height = int(self.height)
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
         
        
        res_img = cv2.resize(file, dsize = (c_width, c_height))

        ret, img_thresh = cv2.threshold(res_img, threshold, 255, cv2.THRESH_BINARY)
        img_thresh = np.where(img_thresh == (0), (40), (255))

        
        cv2.imwrite('nurie.png', img_thresh)
        
        
        
        cv_image = CoreImage.load("nurie.png")
        cv_image = cv_image.texture
        
        with self.canvas:
            Rectangle(texture=cv_image, pos=(0, 0), size=(c_width, c_height))
        
        width_canvas = self.ids.main_canvas.width 
        hight_root = self.height

        print(width_canvas)

        self.export_to_png('temp.png')

        
        raw_image = Image.open('temp.png')
        cuted_image = raw_image.crop((0, 0, width_canvas, hight_root))
        cuted_image = cv2.cvtColor(np.array(cuted_image), cv2.COLOR_BGRA2RGB)
        cuted_image = cv2.flip(cuted_image, 0, cuted_image)
        self.image_history.append(np.array(cuted_image))
        self.load_state = True

class GalleryScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.img_path = './saves/'
        try:
            self.img_list = [os.path.join(self.img_path, f) for f in os.listdir(self.img_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
        except:
            os.mkdir('./saves/')
            self.img_list = [os.path.join(self.img_path, f) for f in os.listdir(self.img_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
        self.page_count = 1
        self.gallery_id = self.ids.gallery_page
        # GridLayoutを作成
        self.page_g = ScreenManager()

        self.images_per_page = 6
        # 画像ファイルをGridLayoutに配置
        self.img_count = len(self.img_list)
        self.img_groups = [self.img_list[i:i+self.images_per_page] for i in range(0, len(self.img_list), self.images_per_page)]

        self.MDGpage = []
        
        for i in range(math.ceil(self.img_count/6)):
            self.MDGpage.append(MDScreen(name='page' + str(i+1)))
        
        self.count_grid = 0
        for i in range(math.ceil(self.img_count/6)):
            gird = MDGridLayout(cols=3, rows=2)
            
            for j in range(6):
                try:
                    gird.add_widget(KvImage(source=self.img_list[self.count_grid]))
                    self.count_grid += 1
                except:
                    break
            self.MDGpage[i].add_widget(gird)
            

        for i in range(math.ceil(self.img_count/6)):
            self.page_g.add_widget(self.MDGpage[i]) 
        self.gallery_id.add_widget(self.page_g)
        
        
        if self.img_count % 6 == 0:
            cur_page = "page" + str(int(self.img_count/6))
            self.page_g.current = cur_page
            self.page_count = int(self.img_count/6)

        else:
            cur_page = "page" + str(int(self.img_count/6)+1)
            self.page_g.current = cur_page
            self.page_count = int((self.img_count/6)+1)

    def rebuild_gallery(self):
        
        
        self.ids.gallery_page.clear_widgets()
        
        self.img_path = './saves/'
        self.img_list = [os.path.join(self.img_path, f) for f in os.listdir(self.img_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
        self.page_count = 1
        self.gallery_id = self.ids.gallery_page
        # GridLayoutを作成
        self.page_g = ScreenManager()

        self.images_per_page = 6
        # 画像ファイルをGridLayoutに配置
        self.img_count = len(self.img_list)
        self.img_groups = [self.img_list[i:i+self.images_per_page] for i in range(0, len(self.img_list), self.images_per_page)]

        self.MDGpage = []
        
        for i in range(math.ceil(self.img_count/6)):
            self.MDGpage.append(MDScreen(name='page' + str(i+1)))

        self.count_grid = 0
        for i in range(math.ceil(self.img_count/6)):
            gird = MDGridLayout(cols=3, rows=2)
            
            for j in range(6):
                try:
                    gird.add_widget(KvImage(source=self.img_list[self.count_grid]))
                    self.count_grid += 1
                except:
                    break
            self.MDGpage[i].add_widget(gird)
            

        for i in range(math.ceil(self.img_count/6)):
            self.page_g.add_widget(self.MDGpage[i]) 
        self.gallery_id.add_widget(self.page_g)
        
        if self.img_count % 6 == 0:
            cur_page = "page" + str(int(self.img_count/6))
            self.page_g.current = cur_page
            self.page_count = int(self.img_count/6)

        else:
            cur_page = "page" + str(int(self.img_count/6)+1)
            self.page_g.current = cur_page
            self.page_count = int((self.img_count/6)+1)

    def page_next(self):
        if self.page_count < self.img_count/6:
            self.page_count += 1
            cur_page = "page" + str(self.page_count)
            self.page_g.transition.direction = 'left'
            self.page_g.current = cur_page

    def page_prev(self):
        if self.page_count != 1:
            self.page_count -= 1
            cur_page = "page" + str(self.page_count)
            self.page_g.transition.direction = 'right'
            self.page_g.current = cur_page

class SelectScreen(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    


class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Olive"  # "Purple", "Red"
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(MenuScreen(name='main'))
        sm.add_widget(SelectScreen(name='select'))
        sm.add_widget(PainterScreen(name='painter'))
        sm.add_widget(GalleryScreen(name='gallery'))
        return sm
    
    def on_resume(self, *args):
        self.theme_cls.set_colors()

    def set_dynamic_color(self, *args) -> None:
        self.theme_cls.dynamic_color = True
        
    def on_stop(self):
        global gl_save_count
        print(gl_save_count)
        for i in range(gl_save_count):
            os.remove("./tmp/" + str(i) + "imga.png")
        try:
            os.remove('temp.png')
        except:
            pass
        try:
            os.remove('temp2.png')
        except:
            pass
        try:
            os.remove('temp3.png')
        except:
            pass
        try:
            os.remove('nurie.png')
        except:
            pass

if __name__ == '__main__':
    MainApp().run()