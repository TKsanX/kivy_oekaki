from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # メインScreenManagerの画面遷移ボタン
        main_btn1 = Button(text='Go to Main Screen 2', on_press=lambda x: self.manager.current='main2')
        main_btn2 = Button(text='Go to Sub Screen Manager', on_press=lambda x: self.manager.current='main2')
        
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(main_btn1)
        layout.add_widget(main_btn2)
        
        # サブScreenManagerを作成してメインScreenに追加
        sub_screen_manager = ScreenManager()
        sub_screen1 = Screen(name='sub1')
        sub_screen2 = Screen(name='sub2')
        sub_screen_manager.add_widget(sub_screen1)
        sub_screen_manager.add_widget(sub_screen2)
        
        layout.add_widget(sub_screen_manager)
        
        self.add_widget(layout)

class MainScreen2(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        btn = Button(text='Go to Main Screen 1', on_press=lambda x: self.manager.current='main1')
        self.add_widget(btn)

class ScreenManagerApp(App):
    def build(self):
        # メインScreenManagerを作成
        root = ScreenManager()
        
        # メインScreenManagerにScreenを追加
        main_screen1 = MainScreen(name='main1')
        main_screen2 = MainScreen2(name='main2')
        root.add_widget(main_screen1)
        root.add_widget(main_screen2)
        
        return root

if __name__ == '__main__':
    ScreenManagerApp().run()