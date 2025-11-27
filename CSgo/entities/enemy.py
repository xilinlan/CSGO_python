# entities/enemy.py
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

class EnemyBullet(Entity):
    def __init__(self, position, direction, player_ref):
        super().__init__(
            model='sphere',
            color=color.orange,
            scale=0.3,
            position=position,
            double_sided=True
        )
        self.player_ref = player_ref
        self.direction = direction
        self.speed = 15
        self.lifetime = 3
        Entity(parent=self, model='sphere', color=color.yellow, scale=0.7, billboard=True)

    def update(self):
        if not self.enabled: return
        self.position += self.direction * self.speed * time.dt
        self.lifetime -= time.dt
        
        if self.lifetime <= 0:
            safe_destroy(self)
            return

        if self.player_ref and self.player_ref.enabled:
            dist_sq = (self.position - (self.player_ref.position + Vec3(0,1.5,0))).length_squared()
            if dist_sq < 2.25:
                self.player_ref.take_damage(Config.ENEMY_DMG)
                safe_destroy(self)

class Enemy(Entity):
    def __init__(self, position=(0,0,0), player_target=None):
        super().__init__(position=position, name='enemy')
        self.player = player_target
        self.hp = Config.ENEMY_HP
        self.max_hp = Config.ENEMY_HP
        self.cooldown_t = 2
        
        # 身体
        self.body = Entity(parent=self, model='cube', color=color.red, scale=(1, 2, 1), 
                           position=(0, 1, 0), collider='box', texture='white_cube')
        
        # 枪
        self.gun_model = Entity(parent=self.body, position=(0.4, 0.2, 0.5), scale=0.3)
        Entity(parent=self.gun_model, model='cube', scale=(0.2, 0.2, 1.5), color=color.dark_gray)
        
        # --- 新增：头顶血条 ---
        # billboard=True 让它始终面向摄像机
        self.health_bar_parent = Entity(parent=self, position=(0, 2.5, 0), billboard=True)
        
        # 黑色背景条
        Entity(parent=self.health_bar_parent, model='quad', color=color.black, scale=(1.2, 0.15))
        
        # 绿色血条 (origin_x=-0.5 让它从左向右缩放)
        # 初始 x=-0.6 是为了对齐背景的最左边 (背景宽1.2，一半是0.6)
        self.hp_bar = Entity(parent=self.health_bar_parent, model='quad', color=color.lime, 
                             scale=(1.2, 0.15), origin_x=-0.5, position=(-0.6, 0, -0.01))

        self.sfx_shoot = safe_load_audio('assets/shot.wav')

    def update(self):
        if not self.enabled: return
        if not self.player or not self.player.enabled: return

        dist = distance_xz(self.position, self.player.position)
        self.look_at_2d(self.player.position, 'y')

        if dist > 8: 
            self.position += self.forward * time.dt * Config.ENEMY_SPEED
        
        self.cooldown_t -= time.dt
        if self.cooldown_t <= 0 and dist < 20:
            self.shoot()

    def shoot(self):
        self.cooldown_t = Config.ENEMY_FIRE_RATE + random.uniform(0, 0.5)
        if self.gun_model: self.gun_model.blink(color.yellow, duration=0.1)
        
        if self.sfx_shoot:
            self.sfx_shoot.pitch = random.uniform(0.8, 1.2)
            self.sfx_shoot.play()

        try:
            target_pos = self.player.position + Vec3(0, 1.4, 0)
            start_pos = self.position + Vec3(0, 1.5, 0) + self.forward * 1.5
            
            direction = (target_pos - start_pos).normalized()
            direction.x += random.uniform(-0.1, 0.1)
            direction.y += random.uniform(-0.1, 0.1)
            
            EnemyBullet(position=start_pos, direction=direction.normalized(), player_ref=self.player)
        except:
            pass

    def take_damage(self, amount):
        if not self.enabled: return
        
        self.hp -= amount
        
        # --- 更新血条 ---
        if self.hp_bar:
            ratio = max(0, self.hp / self.max_hp)
            # 调整 x 轴缩放，最大宽度是 1.2
            self.hp_bar.scale_x = 1.2 * ratio
            
            # 血量低时变红
            if ratio < 0.3:
                self.hp_bar.color = color.red
            else:
                self.hp_bar.color = color.lime

        self.body.blink(color.white, duration=0.1)
        
        if self.hp <= 0: 
            safe_destroy(self)