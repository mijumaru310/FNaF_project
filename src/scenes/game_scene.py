import json
import pygame
from pygame.locals import *
from src.core.base_scene import BaseScene
from src.entities.player import Player
from src.entities.enemy import StandardEnemy, FastEnemy # 敵クラスをインポート
from src.scenes.gameover_scene import GameOverScene
from src.ai.ai_controller import AIController
from src.entities.button import Button
class GameScene(BaseScene):
    def __init__(self, manager):
        self.manager = manager
        with open('config/stages.json', 'r') as f:
            # 今回は第1夜(night_1)のデータを読み込む
            self.stage_data = json.load(f)["night_1"] 
            
        # JSONのデータを渡して初期化
        self.player = Player(decrease_rate=self.stage_data["power_decrease_rate"]) 
        self.font = pygame.font.SysFont(None, 48)

        self.btn_left = Button(50, 450, 150, 50, "L-Door (A)", self.font)
        self.btn_right = Button(600, 450, 150, 50, "R-Door (D)", self.font)
        self.btn_camera = Button(325, 500, 150, 50, "Camera", self.font)
        self.ai = AIController('models/nn_model.keras')

        try:
            self.bg_image = pygame.image.load("assets/images/background.png").convert()
            # 画面サイズ(例：800x600)に合わせて拡大縮小
            self.bg_image = pygame.transform.scale(self.bg_image, (800, 600))
        except FileNotFoundError:
            self.bg_image = None # 画像がない場合は後で単色塗りつぶしにする
        
        # 複数のSpriteをまとめて管理するための入れ物(Group) [1]
        self.all_sprites = pygame.sprite.Group()
        
        # 敵を生成してグループに追加
        self.enemies = [
            StandardEnemy(self.player,ai_controller=self.ai),
            FastEnemy(self.player,ai_controller=self.ai)
        ]
        #self.enemy = Enemy(self.player, interval=self.stage_data["enemy_move_interval"], ai_controller=self.ai)
        self.all_sprites.add(self.enemies, self.enemies[1])
        self.all_sprites.add(self.btn_left, self.btn_right, self.btn_camera)

    def process_event(self, event):
        """キーボードの入力イベントを処理"""
        if event.type == KEYDOWN:
            if event.key == K_a: self.player.left_door_closed = not self.player.left_door_closed
            elif event.key == K_d: self.player.right_door_closed = not self.player.right_door_closed
            elif event.key == K_SPACE: self.player.camera_active = not self.player.camera_active
            elif event.key == K_q:
                self.player.left_light_active = not self.player.left_light_active
                if self.player.right_light_active==True:
                    self.player.right_light_active=False
            elif event.key == K_e:
                self.player.right_light_active = not self.player.right_light_active
                if self.player.left_light_active ==True:
                    self.player.left_light_active=False
            # ★追加：0〜6キーでカメラを切り替える
            elif event.key == K_0: self.player.current_camera_id = 0
            elif event.key == K_1: self.player.current_camera_id = 1
            elif event.key == K_2: self.player.current_camera_id = 2
            elif event.key == K_3: self.player.current_camera_id = 3
            elif event.key == K_4: self.player.current_camera_id = 4
            elif event.key == K_5: self.player.current_camera_id = 5
            elif event.key == K_6: self.player.current_camera_id = 6
            
        elif event.type == MOUSEBUTTONDOWN:
            # 押されたマウスの座標(event.pos)を取得して判定 [2]
            if self.btn_left.is_clicked(event.pos):
                self.player.left_door_closed = not self.player.left_door_closed
            elif self.btn_right.is_clicked(event.pos):
                self.player.right_door_closed = not self.player.right_door_closed
            elif self.btn_camera.is_clicked(event.pos):
                self.player.camera_active = not self.player.camera_active

    def update(self, dt):
        """状態の更新"""
        self.player.update(dt)
        # Group内の全スプライトのupdate()が一括で呼ばれる [1]
        self.all_sprites.update(dt)
        
        # ★ゲームオーバー判定
        for enemy in self.enemies:
            if enemy.is_attacking:
                self.manager.change_scene(GameOverScene(self.manager))
            
        # 電力が0になった場合もゲームオーバー
        if self.player.power <= 0:
            self.manager.change_scene(GameOverScene(self.manager))

    def draw(self, screen):
        """画面の描画"""
        #screen.fill((30, 30, 30)) 

        if self.bg_image:
            # 背景画像を画面の左上(0, 0)から貼り付ける
            screen.blit(self.bg_image, (0, 0))
        else:
            # 画像がない場合は今まで通りのグレー背景
            screen.fill((30, 30, 30)) 
            
        self.all_sprites.draw(screen)

        # Group内の全スプライトが一括で描画される [1]
        self.all_sprites.draw(screen)

        # UIの描画（前回から変更なし）
        power_text = self.font.render(f"Power: {int(self.player.power)}%", True, (255, 255, 255))
        left_door = "CLOSED" if self.player.left_door_closed else "OPEN"
        right_door = "CLOSED" if self.player.right_door_closed else "OPEN"
        if self.player.camera_active:
            camera = f"ACTIVE (Room: {self.player.current_camera_id})"
        else:
            camera = "OFF"

        door_text = self.font.render(f"L-Door: {left_door} | R-Door: {right_door}", True, (200, 200, 200))
        camera_text = self.font.render(f"Camera: {camera}", True, (200, 200, 200))

        l_light = "ON" if self.player.left_light_active else "OFF"
        r_light = "ON" if self.player.right_light_active else "OFF"
        light_text = self.font.render(f"L-Light(Q): {l_light} | R-Light(E): {r_light}", True, (255, 255, 100))

        screen.blit(power_text, (20, 20))
        screen.blit(door_text, (20, 70))
        screen.blit(camera_text, (20, 120))
        screen.blit(light_text, (20, 170)) 

        warning_msg = ""
        for enemy in self.enemies:
            # 誰かが左(3,5)にいて、左ライトがONなら
            if self.player.left_light_active and enemy.position_id in [3, 5]:
                warning_msg = f"!! Enemy in LEFT {self.enemy.position_id} !! "
            # 誰かが右(4,6)にいて、右ライトがONなら
            elif self.player.right_light_active and enemy.position_id in [4, 6]:
                warning_msg = f"!! Enemy in RIGHT {self.enemy.position_id}!! "

        if warning_msg:
            # 警告を赤文字で画面中央に大きく表示
            warn_surface = self.font.render(warning_msg, True, (255, 50, 50))
            warn_rect = warn_surface.get_rect(center=(400, 300))
            screen.blit(warn_surface, warn_rect)