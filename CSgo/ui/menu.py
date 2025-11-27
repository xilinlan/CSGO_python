# ui/menu.py
from ursina import *

class MainMenu(Entity):
    def __init__(self, start_callback, exit_callback):
        super().__init__(parent=camera.ui)
        self.main_panel = Entity(parent=self, enabled=True)
        
        # 背景
        Entity(parent=self.main_panel, model='quad', scale=(2, 1), color=color.black66)

        # 标题
        Text(parent=self.main_panel, text='CS:GO PYTHON', origin=(0,0), scale=3, y=0.25)

        # 按钮
        Button(parent=self.main_panel, text='PLAY', color=color.azure, scale=(0.25, 0.05), y=0, on_click=start_callback)
        Button(parent=self.main_panel, text='EXIT', color=color.red, scale=(0.25, 0.05), y=-0.1, on_click=exit_callback)

    def show(self):
        self.main_panel.enabled = True
        mouse.locked = False # 解锁鼠标以便点击

    def hide(self):
        self.main_panel.enabled = False
        mouse.locked = True # 锁定鼠标用于FPS视角