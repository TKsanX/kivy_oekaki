from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.pagelayout import PageLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.pagelayout import PageLayout
from kivy.uix.image import Image as KvImage


from kivy.graphics.texture import Texture
from kivy.core.image import Image as CoreImage
import gc
import cv2
import numpy as np

import os

import threading as th
from kivy.core.window import Window

from PIL import Image
from PIL.PngImagePlugin import PngInfo

from collections import deque


import json

import time

'''
#! メモ
#* 塗り絵にする
#* 塗り絵のSVGの自動生成
#* diffusersや写真から縁検出

#* やることリスト
#* ・塗りつぶしの実装
#* ・SVGの生成
#* ・ギャラリーの実装
#* ・ワンクリック入力
#* ・
'''
'''
#! つまずいたことリスト（解決済み）
kivyのレイアウトがうまくいかない
    日本圏の情報が少なすぎて地獄

on_touch_downのtouch.xとtouch.yは一番左下が0,0になる
    →左下が0,0かと思った...入れ替えて対応

canvasからは直接色を取得できない
    →一度temp.pngを出力してからクリックした座標のカラーコードを取得する

画像保存時にメタデータを埋め込めない
    →一度画像をファイルに保存してから読み込み埋め込む

保存したjsonを読み込む際にcanvasをclearすると背景色までリセットされてしまう
    →clearを使わず書いたものがなくなるまでundoする（これでいいのかは知らんし多分いつかバグる）

undo処理時に色が適応されない
    →color_histoy変数を作成し対応、jsonにもappend時に記載するように

画面サイズ変更時に描画外にはみ出る
    →無理、画面サイズ変更時に変更倍率を各Lineの座標にかければうまくいきそうだが各座標はint型で保存しているため小さくしてから戻した時値が返送する可能性があるため
    同じ絵を描き続ける場合は画面サイズを変更しないようにしてもらう
#!  一度保存したデータを読み込む際も同様、読み込み時にサイズが違う場合は警告通知を流すように対応する(未実装)

一回塗りつぶしを実行すると2回目以降texture変数を初期化しても一回目と同じところしか塗れない
    →opengl内部でtextureがキャッシュされてしまうのが原因。
    ファイル名がキャッシュのキーになっているためクリックごとに増加するカウント変数を用意しファイル名に付与することで解決
    textureをリロードする関数はあるそうだが使い方を知らないためpass
    だいぶというかかなり無理やりなためこれでいいのかは知らん

'''


color_picker = (0, 0, 0, 1)
gl_save_count = 0
#! デバッグ用モード切替
#! 0:塗りつぶしモード
#! 1:描画モード
write_mode = 0

class PaintWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.drawing = False
        self.stroke = []
        self.undo_strokes = []
        self.color_history = []
        self.save_count = 0
        self.image_history = [] 

    '''
    #* タッチイベント
    #* downは押された時
    #* moveはdown後に動いたとき
    #* upは離したとき
    #! 要修正 塗りつぶしの実装
    #! 
    
    '''
    
    def on_image1_down(self, touch):
        if write_mode == 0:
            if self.collide_point(*touch.pos):
                self.fill(touch)
        else:
            global color_picker
            if self.collide_point(*touch.pos):
                with self.canvas:
                    Color(rgba=color_picker)
                    self.color_history.append(color_picker)
                    touch.ud['line'] = Line(points=(touch.x, touch.y), width=2, rgba=(0, 0, 0, 0))
                self.drawing = True
        
    
    
    def fill(self, touch):
        global color_picker
        global gl_save_count
        x = touch.x
        y = touch.y

        
        self.export_to_png('temp.png')
        bgr_array = cv2.imread('temp.png')
        image_shape = bgr_array.shape
        fix_y = abs(int(y) - image_shape[0])
        
        temp1 = cv2.imread('temp.png')
        
        if color_picker == (0, 0, 0, 1):
            fill_mode = 1
        else:
            fill_mode = 0
        
        color_picker_255 = tuple(component * 255 for component in color_picker[:3])
        color_picker_255 = color_picker_255[::-1]

        cv2.floodFill(bgr_array,None , (int(x), int(fix_y)), (255,0,0))
        cv2.imwrite('temp2.png', bgr_array)
        
        #差分を取得する
        diff = cv2.absdiff(temp1, bgr_array, 0)
        diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        ret, diff = cv2.threshold(diff, 1, 255, cv2.THRESH_BINARY)
        diff = cv2.bitwise_not(diff)
        diff = cv2.cvtColor(diff, cv2.COLOR_GRAY2BGR)

        img = np.where(diff == (0, 0, 0), color_picker_255, (255, 255, 255))
        
        mask = np.all(img[:,:,:] == [255, 255, 255], axis=-1)
        
        #cv2.imwrite('mask.png', mask)
        
        img_rgba = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_BGR2BGRA)
        img_rgba[mask,3] = 0
        
        save_img_name = str(self.save_count) + "imga.png"
        
        cv2.imwrite(save_img_name, img_rgba)
        
        cv_image = CoreImage.load(save_img_name)
        cv_image = cv_image.texture
        self.save_count += 1
        gl_save_count = self.save_count
        print(self.save_count)
        
        with self.canvas:
            self.color_history.append(color_picker)

            Color(rgba=color_picker)
            touch.ud['image'] = Rectangle(texture=cv_image, pos=(0, 0), size=(image_shape[1], image_shape[0]))
        self.image_history.append(img_rgba)
        self.drawing = True
        
        del bgr_array
        del temp1
        del diff
        del img
        del mask
        del img_rgba
        del cv_image
        gc.collect()
        
        
        #cv2.imwrite('img.png', img)
        """
        print("縦:" + str(image_shape[0]))
        print("横:" + str(image_shape[1]))
        
        print(int(fix_y))
        print(int(x))
        print(bgr_array[int(fix_y), int(x), :])
        
        print(int(x),int(fix_y))
        """
        """
        fix_y が縦軸
        x が横軸
        """
    
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
            self.undo_strokes.append(stroke)
            self.canvas.remove(stroke)
            

    '''
    #! 仮実装 
    #! 簡易セーブ機能
    #* 多分うまく動かん
    #! いずれ画像にテキストを埋め込む形で進める
    #* 色の保存V
    '''
    def save_canvas_data(self):
        if write_mode == 0:
            canvas_data = []
            count = 0
            for i in self.image_history:
                color = self.color_history[count]
                images= self.image_history[count]
                
                canvas_data.append({'image': images, 'color': color})
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
        


class ButtonWidget(GridLayout):
    '''
    #! 要修正
    #! 無理やり実装カラーチェンジ
    #! global使いすぎ
    '''
    def color_change_black(self):
        global color_picker
        color_picker = (0, 0, 0, 1)
        print(color_picker)
    def color_change_red(self):
        global color_picker
        color_picker = (1, 0, 0, 1)
        print(color_picker)
    def color_change_green(self):
        global color_picker
        color_picker = (0, 1, 0, 1)
        print(color_picker)
    def color_change_blue(self):
        global color_picker
        color_picker = (0, 0, 1, 1)
        print(color_picker)
        
    
    def test_code(self):
        pass

class galleryApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.img_path = './saves/'
        self.img_list = [os.path.join(self.img_path, f) for f in os.listdir(self.img_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
        self.page_count = 1

        # GridLayoutを作成
        self.page = PageLayout(border=0)

        def next_page(instance):
            self.page_layout.next_page()

        self.images_per_page = 4
        # 画像ファイルをGridLayoutに配置
        self.img_count = len(self.img_list)

        self.img_groups = [self.img_list[i:i+self.images_per_page] for i in range(0, len(self.img_list), self.images_per_page)]


        for group in self.img_groups:
            grid = GridLayout(cols=2, rows=2)
            for path in group:
                image = KvImage(source=path)
                grid.add_widget(image)
            self.page.add_widget(grid)

        # GridLayoutをルートウィジェットに追加
        self.add_widget(self.page)

    def n_page(self):
        if self.page_count != 0 and int(self.page_count) <= int(len(self.img_list)/4):
            self.page_count += 1
            self.page.next_page()
    def p_page(self):
        self.page_count-= 1

    


class PaintApp(App):
    def build(self):
        parent = BoxLayout()
        self.painter = PaintWidget()
        self.buttons = ButtonWidget()
        self.gallery = galleryApp()
        
        parent.add_widget(self.painter)
        parent.add_widget(self.buttons)
        parent.add_widget(self.gallery)
        
        #! 仮セーブボタン
        save_button = Button(text="Save", size_hint=(0.1, 0.1), pos_hint={'x': 0.7, 'y': 0.9})
        save_button.bind(on_press=self.save_canvas)
        parent.add_widget(save_button)

        #! 仮ロードボタン
        load_button = Button(text="Load", size_hint=(0.1, 0.1), pos_hint={'x': 0.6, 'y': 0.9})
        load_button.bind(on_press=self.load_canvas)
        parent.add_widget(load_button)
        
        
        return parent
    def on_stop(self):
        global gl_save_count
        print(gl_save_count)
        for i in range(gl_save_count):
            os.remove(str(i) + "imga.png")
        os.remove('temp.png')
        os.remove('temp2.png')
        
    
    '''
    #! 保存処理
    #! 仮実装
    #! ビューワーの実装やcanvasそのものの保存が必要
    '''
    def save_image_canvas(self):
        now_time = time.strftime('%Y%m%d%H%M%S', time.localtime())
        fl_name = './saves/image_' + now_time + '.png'
        self.painter.export_to_png(fl_name)
        tmp_image = Image.open(fl_name)

        metadata = PngInfo()
        metadata.add_text('data', now_time)
        metadata.add_text('LineJson', str(self.painter.save_canvas_data()))
        tmp_image.save(fl_name, pnginfo=metadata)
        
        
    def save_canvas(self, instance):
        canvas_data = self.painter.save_canvas_data()
        with open('canvas.json', 'w') as f:
            json.dump(canvas_data, f)


    def load_canvas(self, instance):
        try:
            with open('canvas.json', 'r') as f:
                canvas_data = json.load(f)
            self.painter.load_canvas_data(canvas_data)
        except FileNotFoundError:
            pass
if __name__ == '__main__':
    PaintApp().run()