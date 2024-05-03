from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.pagelayout import PageLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line
import cv2
import numpy as np

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


'''


color_picker = (0, 0, 0, 1)

class PaintWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.drawing = False
        self.stroke = []
        self.undo_strokes = []
        self.color_history = []

    '''
    #* タッチイベント
    #* downは押された時
    #* moveはdown後に動いたとき
    #* upは離したとき
    #! 要修正 塗りつぶしの実装
    #! 
    
    '''
    
    def on_image1_down(self, touch):
        
        
        self.fill(touch.x, touch.y)

        '''
        global color_picker
        if self.collide_point(*touch.pos):
            with self.canvas:
                Color(rgba=color_picker)
                self.color_history.append(color_picker)
                touch.ud['line'] = Line(points=(touch.x, touch.y), width=2, rgba=(0, 0, 0, 0))
            self.drawing = True
        '''
    
    
    def fill(self, x, y):
        
        self.export_to_png('temp.png')
        bgr_array = cv2.imread('temp.png')
        image_shape = bgr_array.shape
        
        
        print("縦:" + str(image_shape[0]))
        print("横:" + str(image_shape[1]))
        print(int(x))
        print(int(y))
        #print(bgr_array[int(x), int(y), :])
        



    
    def on_image1_move(self, touch):
        if self.drawing:
            touch.ud["line"].points += [touch.x, touch.y]
    
    def on_image1_up(self, touch):
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
        canvas_data = []
        count = 0
        for stroke in self.stroke:
            color = self.color_history[count]
            count += 1
            points = [round(p, 2) for p in stroke.points]
            width = round(stroke.width, 2)
            canvas_data.append({'points': points, 'width': width, 'color': color})
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
    pass



class PaintApp(App):
    def build(self):
        parent = BoxLayout()
        self.painter = PaintWidget()
        self.buttons = ButtonWidget()
        self.gallery = galleryApp()
        
        parent.add_widget(self.painter)
        parent.add_widget(self.buttons)
        
        #! 仮セーブボタン
        save_button = Button(text="Save", size_hint=(0.1, 0.1), pos_hint={'x': 0.7, 'y': 0.9})
        save_button.bind(on_press=self.save_canvas)
        parent.add_widget(save_button)

        #! 仮ロードボタン
        load_button = Button(text="Load", size_hint=(0.1, 0.1), pos_hint={'x': 0.6, 'y': 0.9})
        load_button.bind(on_press=self.load_canvas)
        parent.add_widget(load_button)
        
        
        return parent
    
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