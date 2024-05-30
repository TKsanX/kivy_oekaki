from kivymd.app import MDApp
from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText
from kivymd.uix.screen import MDScreen
from kivy.uix.button import Button


class Example(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Green"
        btn1 = Button(text='Hello world 1')
        btn1.bind(on_press=callback)
        btn2 = Button(text='Hello world 2')
        btn2.bind(on_press=callback)
        def callback(instance):
            print('The button <%s> is being pressed' % instance.text)

Example().run()