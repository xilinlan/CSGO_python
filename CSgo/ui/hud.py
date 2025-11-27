# ui/hud.py
from ursina import *
from core.config import Config

class HUD(Entity):
    def __init__(self):
        super().__init__(parent=camera.ui)
        # 准星
        self.crosshair = Entity(parent=self, model='quad', color=color.green, scale=0.005, rotation_z=45)
        
        # 弹药显示
        self.ammo_text = Text(parent=self, text='30 / 30', position=(0.7, -0.4), scale=2, origin=(0,0))
        
        # 血条背景
        self.hp_bar_bg = Entity(parent=self, model='quad', color=color.gray, scale=(0.4, 0.02), position=(-0.6, -0.4), origin=(-0.5, 0))
        # 实际血条
        self.hp_bar = Entity(parent=self, model='quad', color=color.lime, scale=(0.4, 0.02), position=(-0.6, -0.4), origin=(-0.5, 0))
        self.hp_text = Text(parent=self, text='HP: 100', position=(-0.6, -0.35), scale=1.5)

        # 受伤红色遮罩
        self.damage_overlay = Entity(parent=self, model='quad', scale=(2, 1), color=color.red, alpha=0)

        # --- 性能优化：记录上一次的值，防止每一帧都重绘文字 ---
        self._last_ammo = -1
        self._last_hp = -1

    def update_ammo(self, current, max_ammo):
        # 只有数值变了才更新 UI
        if current != self._last_ammo:
            self.ammo_text.text = f'{current} / {max_ammo}'
            self._last_ammo = current

    def update_hp(self, current_hp, max_hp):
        # 只有数值变了才更新 UI
        if current_hp != self._last_hp:
            current_hp = max(0, current_hp)
            ratio = current_hp / max_hp
            self.hp_bar.scale_x = 0.4 * ratio
            self.hp_text.text = f'HP: {int(current_hp)}'
            
            if ratio < 0.3:
                self.hp_bar.color = color.red
            else:
                self.hp_bar.color = color.lime
            
            self._last_hp = current_hp

    def show_damage_effect(self):
        self.damage_overlay.alpha = 0.5
        self.damage_overlay.animate('alpha', 0, duration=0.5)