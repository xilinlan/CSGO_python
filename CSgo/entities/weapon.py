# entities/weapon.py
from ursina import *
from core.config import Config
from core.utils import safe_load_audio
import random

def safe_destroy(entity):
    if not entity: return
    entity.visible = False
    entity.enabled = False
    entity.position = (0, -10000, 0)
    destroy(entity, delay=1)

class PlayerBullet(Entity):
    # 新增 hit_sound 参数
    def __init__(self, position, direction, hit_sound=None):
        super().__init__(
            model='sphere',
            color=color.cyan,
            scale=0.15,
            position=position,
            double_sided=True
        )
        self.direction = direction
        self.speed = 80 
        self.lifetime = 2.0
        self.hit_sound = hit_sound # 存储音效引用
        
        self.trail = Entity(parent=self, model='cube', scale=(0.1, 0.1, 2), color=color.cyan, alpha=0.5, z=-1)

    def update(self):
        if not self.enabled: return
        self.position += self.direction * self.speed * time.dt
        self.lifetime -= time.dt
        
        if self.lifetime <= 0:
            safe_destroy(self)
            return

        for e in list(scene.entities):
            if not e or not e.enabled: continue
            if e.name == 'enemy':
                dist_sq = (e.position - self.position).length_squared()
                if dist_sq < 3.0:
                    if hasattr(e, 'take_damage'):
                        e.take_damage(Config.DMG)
                        
                        # --- 播放击中音效 ---
                        if self.hit_sound:
                            self.hit_sound.pitch = random.uniform(0.9, 1.1)
                            self.hit_sound.stop()
                            self.hit_sound.play()
                            
                        safe_destroy(self)
                        return

class AK47(Entity):
    def __init__(self, parent_camera):
        super().__init__(parent=parent_camera)
        
        self.gun_root = Entity(parent=self, position=(0.5, -0.4, 0.6), scale=0.5)
        
        # 枪模
        Entity(parent=self.gun_root, model='cube', scale=(0.1, 0.15, 0.8), color=color.dark_gray)
        Entity(parent=self.gun_root, model='cube', scale=(0.08, 0.4, 0.15), position=(0, -0.2, 0), rotation=(-15,0,0), color=color.black)
        Entity(parent=self.gun_root, model='cube', scale=(0.05, 0.05, 0.4), position=(0, 0.05, 0.6), color=color.black)
        Entity(parent=self.gun_root, model='cube', scale=(0.02, 0.05, 0.02), position=(0, 0.1, 0.75), color=color.black)
        Entity(parent=self.gun_root, model='cube', scale=(0.1, 0.2, 0.3), position=(0, -0.05, -0.5), color=color.brown)

        self.muzzle_flash = Entity(parent=self.gun_root, model='quad', color=color.yellow, scale=0.3, position=(0, 0.1, 1.2), enabled=False, billboard=True, texture='circle')

        self.ammo = Config.AMMO
        self.on_cooldown = False
        
        # 加载音效
        self.sfx_shoot = safe_load_audio('assets/shot.wav')
        self.sfx_reload = safe_load_audio('assets/reload.wav')
        self.sfx_hit = safe_load_audio('assets/hit.wav') # 新增 hit.wav

    def shoot(self):
        if self.ammo <= 0: return

        if not self.on_cooldown:
            self.on_cooldown = True
            self.ammo -= 1
            
            if self.sfx_shoot:
                self.sfx_shoot.pitch = random.uniform(0.9, 1.1)
                self.sfx_shoot.play()
            
            self.gun_root.animate_position((0.5, -0.35, 0.4), duration=0.05, curve=curve.linear)
            self.gun_root.animate_rotation((-10, 0, 0), duration=0.05)
            
            self.muzzle_flash.enabled = True
            invoke(setattr, self.muzzle_flash, 'enabled', False, delay=0.05)
            
            spawn_pos = camera.world_position + camera.forward * 1.5
            # 传入 sfx_hit
            PlayerBullet(position=spawn_pos, direction=camera.forward, hit_sound=self.sfx_hit)

            invoke(self.gun_root.animate_position, (0.5, -0.4, 0.6), duration=0.1, delay=0.05)
            invoke(self.gun_root.animate_rotation, (0, 0, 0), duration=0.1, delay=0.05)
            
            invoke(setattr, self, 'on_cooldown', False, delay=Config.FIRE_RATE)

    def reload(self):
        self.ammo = Config.AMMO_CAPACITY
        if self.sfx_reload: self.sfx_reload.play()
        self.gun_root.animate_rotation((30, 0, -30), duration=0.5)
        invoke(self.gun_root.animate_rotation, (0, 0, 0), duration=0.5, delay=0.5)

    def input(self, key):
        if key == 'left mouse down' and mouse.locked: self.shoot()
        if key == 'r': self.reload()