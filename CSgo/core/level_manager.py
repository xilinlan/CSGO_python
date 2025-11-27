# core/level_manager.py
from ursina import *
from entities.enemy import Enemy
from core.config import Config # 导入配置
import random

class LevelManager(Entity):
    # 新增 on_victory_callback 参数
    def __init__(self, player, on_victory_callback=None):
        super().__init__()
        self.player = player
        self.on_victory_callback = on_victory_callback
        
        self.wave = 1
        self.enemies_alive = []
        
        self.spawn_areas = [(-15, -15), (15, 15), (-15, 15), (15, -15)]
        
        self.wave_active = False
        self.time_to_next_wave = 3
        
        self.wave_text = Text(text='', scale=3, origin=(0,0), color=color.yellow, enabled=False)

    def start_wave(self):
        # --- 检查是否通关 ---
        if self.wave > Config.MAX_WAVES:
            if self.on_victory_callback:
                self.on_victory_callback()
            return

        self.wave_active = True
        self.wave_text.text = f'WAVE {self.wave} / {Config.MAX_WAVES}' # 显示进度
        self.wave_text.enabled = True
        invoke(setattr, self.wave_text, 'enabled', False, delay=2)
        
        count = 3 + int(self.wave * 1.5)
        
        for i in range(count):
            area = random.choice(self.spawn_areas)
            x = area[0] + random.randint(-5, 5)
            z = area[1] + random.randint(-5, 5)
            spawn_pos = (x, 0, z) # y=0 地面
            
            e = Enemy(position=spawn_pos, player_target=self.player)
            e.hp *= (1 + self.wave * 0.1)
            self.enemies_alive.append(e)

    def update(self):
        self.enemies_alive = [e for e in self.enemies_alive if e and e.enabled]
        
        if not self.wave_active:
            self.time_to_next_wave -= time.dt
            if self.time_to_next_wave <= 0:
                self.start_wave()
        else:
            if len(self.enemies_alive) == 0:
                self.wave += 1
                self.wave_active = False
                self.time_to_next_wave = 4 
                
                if self.player.hp < 100:
                    self.player.hp = min(100, self.player.hp + 30)