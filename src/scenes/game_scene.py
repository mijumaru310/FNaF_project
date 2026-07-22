import json
import pygame
from pygame.locals import *
import random
from src.core.base_scene import BaseScene
from src.entities.player import Player
from src.entities.enemy import StandardEnemy, FastEnemy # 敵クラスをインポート
from src.scenes.gameover_scene import GameOverScene
from src.scenes.gameclear_scene import GameClearScene
from src.ai.ai_controller import AIController
from src.entities.button import Button
class GameScene(BaseScene):
    def __init__(self, manager,level_id="night_1"):
        self.manager = manager
        self.level_id = level_id 
        with open('config/stages.json', 'r') as f:
            # ★修正：固定の "night_1" ではなく、受け取った level_id のデータを読み込む
            self.stage_data = json.load(f)[level_id]
        speed_mult = self.stage_data.get("enemy_speed_multiplier", 1.0)
        power_mult = self.stage_data.get("power_decrease_multiplier", 1.0)
        self.enemynum = self.stage_data.get("enemy_num",1)
        ai_path = self.stage_data.get("ai_model_path", "models/nn_model_night_1.keras")
            
        # JSONのデータを渡して初期化
        self.player = Player(decrease_rate=2.0 * power_mult)
        self.font = pygame.font.SysFont(None, 48)

        self.btn_left = Button(0, 450, 200, 50, "L-Door (A)", self.font)
        self.btn_right = Button(600, 450, 200, 50, "R-Door (D)", self.font)
        self.btn_camera = Button(325, 500, 150, 50, "Camera", self.font)
        self.btn_closecamera = Button(275, 500, 250, 50, "Close Camera", self.font)
        self.ai = AIController(model_path=ai_path)
        self.SE_door=pygame.mixer.Sound("assets/sounds/door.mp3")
        self.SE_hora=pygame.mixer.Sound("assets/sounds/hora-.mp3")

        self.cam_buttons = {
            0: pygame.Rect(620, 250, 100, 40), # 奥の部屋
            1: pygame.Rect(560, 320, 100, 40), # ダイニング
            2: pygame.Rect(680, 320, 100, 40), # 物置
            3: pygame.Rect(560, 390, 100, 40), # 左通路
            4: pygame.Rect(680, 390, 100, 40), # 右通路
            5: pygame.Rect(560, 460, 100, 40), # 左扉前
            6: pygame.Rect(680, 460, 100, 40)  # 右扉前
        }

        self.light_buttons = {
            "left": pygame.Rect(150, 280, 40, 40), # 中心が(170, 300)の円を囲む四角
            "right": pygame.Rect(610, 280, 40, 40) # 中心が(630, 300)の円を囲む四角
        }

        try:
            self.bg_image = pygame.image.load("assets/images/background.png").convert()
            # 画面サイズ(例：800x600)に合わせて拡大縮小
            self.bg_image = pygame.transform.scale(self.bg_image, (800, 600))
        except FileNotFoundError:
            self.bg_image = None # 画像がない場合は後で単色塗りつぶしにする
        
        self.camera_image=[]
        for i in range(4):
            self.camera_image.append(pygame.image.load(f"assets/images/camera{i}.png").convert())
            self.camera_image[i] = pygame.transform.scale(self.camera_image[i], (800, 600))
        
        #print(f"カメライメージ{len(self.camera_image)}")
        
        #右のドア
        try:
            self.rdoor_image = pygame.image.load("assets/images/rightdoor.png").convert()
            # 画面サイズ(例：800x600)に合わせて拡大縮小
            self.rdoor_image = pygame.transform.scale(self.rdoor_image, (120, 375))
        except FileNotFoundError:
            self.rdoor_image = None # 画像がない場合は後で単色塗りつぶしにする

        #左のドア
        try:
            self.ldoor_image = pygame.image.load("assets/images/leftdoor.png").convert()
            # 画面サイズ(例：800x600)に合わせて拡大縮小
            self.ldoor_image = pygame.transform.scale(self.ldoor_image, (120, 375))
        except FileNotFoundError:
            self.ldoor_image = None # 画像がない場合は後で単色塗りつぶしにする
        
        # 複数のSpriteをまとめて管理するための入れ物(Group) [1]
        self.all_sprites = pygame.sprite.Group()
        self.all_spritesinCamara = pygame.sprite.Group()
        
        # 敵を生成してグループに追加
        if self.enemynum ==1:
            self.enemies = [
            StandardEnemy(self.player,ai_controller=self.ai),
            ]
        elif self.enemynum ==2:
            self.enemies = [
                StandardEnemy(self.player,ai_controller=self.ai),
                FastEnemy(self.player,ai_controller=self.ai)
            ]
        for enemy in self.enemies:
            enemy.move_interval *= speed_mult
        #self.enemy = Enemy(self.player, interval=self.stage_data["enemy_move_interval"], ai_controller=self.ai)
        for enemy in self.enemies:
            self.all_sprites.add(enemy)
        #self.all_sprites.add(self.enemies, self.enemies[1])
        self.all_sprites.add(self.btn_left, self.btn_right, self.btn_camera)
        self.all_spritesinCamara.add(self.btn_closecamera)
         # ★追加：ゲーム内時間の管理 (0 = 12 AM)
        self.game_hour = 0
        self.time_timer = 0.0
        # 1プレイ3分にするため、現実の30秒でゲーム内の1時間が進むように設定
        self.sec_per_hour = 4.0 
    def process_event(self, event):
        """キーボードの入力イベントを処理"""
        if event.type == KEYDOWN:
            if event.key == K_a:
                self.player.left_door_closed = not self.player.left_door_closed
                self.SE_door.play()
            elif event.key == K_d:
                self.player.right_door_closed = not self.player.right_door_closed
                self.SE_door.play()
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
            #カメラを開いているときは反応しないように
            if self.btn_left.is_clicked(event.pos) and not self.player.camera_active:
                self.player.left_door_closed = not self.player.left_door_closed
                self.SE_door.play()
            elif self.btn_right.is_clicked(event.pos) and not self.player.camera_active:
                self.player.right_door_closed = not self.player.right_door_closed
                self.SE_door.play()
            elif self.btn_camera.is_clicked(event.pos) and not self.player.camera_active:
                self.player.camera_active = not self.player.camera_active
            elif self.btn_closecamera.is_clicked(event.pos) and  self.player.camera_active: #カメラ閉じるボタン
                self.player.camera_active = not self.player.camera_active
           

            # ★追加：マウスクリックによるカメラ切り替え処理
            if event.type == MOUSEBUTTONDOWN and event.button == 1: # 左クリック
                if self.player.camera_active:
                    # 定義したすべてのボタンの当たり判定(collidepoint)をチェック
                    for cam_id, rect in self.cam_buttons.items():
                        if rect.collidepoint(event.pos):
                            self.player.current_camera_id = cam_id
                else:
                    # ★追加：警備室にいる時は丸いライトボタンを操作できる
                    if self.light_buttons["left"].collidepoint(event.pos):
                        self.player.left_light_active = not self.player.left_light_active
                    if self.light_buttons["right"].collidepoint(event.pos):
                        self.player.right_light_active = not self.player.right_light_active

    def update(self, dt):
        """状態の更新"""
        self.player.update(dt)
        # Group内の全スプライトのupdate()が一括で呼ばれる [1]
        self.all_sprites.update(dt)
        
        # ★追加：時間の経過処理
        self.time_timer += dt
        if self.time_timer >= self.sec_per_hour:
            self.time_timer = 0.0
            self.game_hour += 1
            
        # ★追加：朝6時(6 AM)になったらクリア画面へ遷移
        if self.game_hour >= 6:
            pygame.mixer.music.stop()
            self.manager.change_scene(GameClearScene(self.manager))
            return # シーン遷移するので以降の処理（ゲームオーバー判定など）はストップ
           

        # ★ゲームオーバー判定
        for enemy in self.enemies:
            if enemy.is_attacking:
                pygame.mixer.music.stop()
                self.manager.change_scene(GameOverScene(self.manager))
            
        # 電力が0になった場合もゲームオーバー
        if self.player.power <= 0:
            pygame.mixer.music.stop()
            self.manager.change_scene(GameOverScene(self.manager))

    def draw(self, screen):
        """画面の描画"""
        #screen.fill((30, 30, 30)) 

        if self.player.camera_active:
            # ==========================================
            # カメラ起動中の描画（モニター映像）
            # ==========================================
            screen.fill((40, 40, 40)) # カメラの背景（暗いグレー）
            cam_id = self.player.current_camera_id
            

            if self.bg_image:
                # 背景画像を画面の左上(0, 0)から貼り付ける
                if cam_id<=3:
                    screen.blit(self.camera_image[cam_id], (0, 0))
                else:
                    screen.blit(self.camera_image[3], (0, 0))
            else:
                # 画像がない場合は今まで通りのグレー背景
                screen.fill((40, 40, 40))

            # 1. 部屋名の表示
            room_names = {
                0: "CAM 0: Back Room ", 1: "CAM 1: Dining ", 
                2: "CAM 2: Storage ",       3: "CAM 3: Left Hall ", 
                4: "CAM 4: Right Hall ",  5: "CAM 5: Left Door ", 
                6: "CAM 6: Right Door "
            }
            room_text = self.font.render(room_names.get(cam_id, "Unknown"), True, (255, 255, 255))
            
            screen.blit(room_text, (350, 20))

            # 2. カメラ映像内に敵を描画（見ている部屋にいる敵だけ）
            enemy_drawn_count = 0
            for enemy in self.enemies:
                if enemy.position_id == cam_id:
                    if cam_id ==0:
                        scaled_img = pygame.transform.scale(enemy.image, (250, 250))
                        screen.blit(scaled_img, (250 + enemy_drawn_count * 100, 350))
                        enemy_drawn_count += 1
                    elif cam_id ==1:
                        scaled_img = pygame.transform.scale(enemy.image, (100, 100))
                        screen.blit(scaled_img, (250 + enemy_drawn_count * 200, 125))
                        enemy_drawn_count += 1
                    elif cam_id ==2:
                        scaled_img = pygame.transform.scale(enemy.image, (100, 100))
                        screen.blit(scaled_img, (250 + enemy_drawn_count * 100, 150))
                        enemy_drawn_count += 1
                    elif cam_id ==3:
                        scaled_img = pygame.transform.scale(enemy.image, (250, 250))
                        screen.blit(scaled_img, (275 , 150+ enemy_drawn_count * 100))
                        enemy_drawn_count += 1
                    elif cam_id ==4:
                        scaled_img = pygame.transform.scale(enemy.image, (250, 250))
                        screen.blit(scaled_img, (275 , 150+ enemy_drawn_count * 100))
                        enemy_drawn_count += 1
                    elif cam_id ==5:
                        scaled_img = pygame.transform.scale(enemy.image, (250, 250))
                        screen.blit(scaled_img, (275 , 150+ enemy_drawn_count * 100))
                        enemy_drawn_count += 1
                    elif cam_id ==6:
                        scaled_img = pygame.transform.scale(enemy.image, (250, 250))
                        screen.blit(scaled_img, (275 , 150+ enemy_drawn_count * 100))
                        enemy_drawn_count += 1



            # 3. カメラのノイズ（走査線）エフェクト
            for y in range(0, 600, 5):
                # ランダムに横線を引いて、古い監視カメラ感を出す
                if random.random() > 0.7:
                    pygame.draw.line(screen, (80, 80, 80), (0, y), (800, y), 1)

            # 4. RECマーク（点滅演出）
            if pygame.time.get_ticks() % 1000 < 500: # 0.5秒ごとに点滅
                pygame.draw.circle(screen, (255, 0, 0), (775, 30), 10)
                rec_text = self.font.render("REC", True, (255, 0, 0))
                screen.blit(rec_text, (690, 15))

            power_text = self.font.render(f"Power: {int(self.player.power)}%", True, (255, 255, 255))
            left_door = "CLOSED" if self.player.left_door_closed else "OPEN"
            right_door = "CLOSED" if self.player.right_door_closed else "OPEN"
            door_text = self.font.render(f"L-Door: {left_door} | R-Door: {right_door}", True, (200, 200, 200))
            screen.blit(power_text, (20, 20))
            screen.blit(door_text, (20, 70))
            self.all_spritesinCamara.draw(screen)

            # 5. 操作ガイド
            guide_text = self.font.render("Press 0-6 to switch CAM / SPACE to close", True, (200, 200, 200))
            screen.blit(guide_text, (20, 550))

             # ★追加：ここからカメラマップ（UI）の描画
            # 1. 部屋のつながりを示す「線」を描画する
            lines = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 4), (3, 5), (4, 6)]
            for start, end in lines:
                start_pos = self.cam_buttons[start].center
                end_pos = self.cam_buttons[end].center
                pygame.draw.line(screen, (200, 200, 200), start_pos, end_pos, 2)
            
            # 2. プレイヤーの現在地（YOU）を描画して線を繋ぐ
            pygame.draw.rect(screen, (150, 150, 150), (620, 530, 100, 30))
            you_text = self.font.render("YOU", True, (0, 0, 0))
            you_rect = you_text.get_rect(center=(650, 545))
            screen.blit(you_text, you_rect)
            pygame.draw.line(screen, (200, 200, 200), self.cam_buttons[5].center, (620, 545), 2)
            pygame.draw.line(screen, (200, 200, 200), self.cam_buttons[6].center, (680, 545), 2)

            # 3. 各カメラのボタンを描画する
            for cam_id, rect in self.cam_buttons.items():
                # 現在見ているカメラの場合は色を緑(Light Green)にする
                is_active = (self.player.current_camera_id == cam_id)
                btn_color = (100, 255, 100) if is_active else (80, 80, 80)
                text_color = (0, 0, 0) if is_active else (255, 255, 255)

                pygame.draw.rect(screen, btn_color, rect)          # ボタン背景
                pygame.draw.rect(screen, (255, 255, 255), rect, 2) # ボタン枠線
                
                # 「CAM 〇」の文字をボタンの中央に描画
                cam_text = self.font.render(f"CAM {cam_id}", True, text_color)
                text_rect = cam_text.get_rect(center=rect.center)
                screen.blit(cam_text, text_rect)

        else:
            if self.bg_image:
                # 背景画像を画面の左上(0, 0)から貼り付ける
                screen.blit(self.bg_image, (0, 0))
            else:
                # 画像がない場合は今まで通りのグレー背景
                screen.fill((30, 30, 30)) 
            
            self.all_sprites.draw(screen)

            if self.player.left_door_closed:
                # 左側に灰色の壁（扉）を描画
                screen.blit(self.ldoor_image, (100, 170))
            if self.player.right_door_closed:
                # 右側に灰色の壁（扉）を描画
                screen.blit(self.rdoor_image, (620, 170))

            # ★追加：2. 丸いライトボタンの描画
            # ライトがONなら明るい黄色、OFFなら暗い色にする
            l_color = (255, 255, 200) if self.player.left_light_active else (80, 80, 80)
            r_color = (255, 255, 200) if self.player.right_light_active else (80, 80, 80)
            
            # 左ライトボタン
            pygame.draw.circle(screen, l_color, (170, 300), 20)
            pygame.draw.circle(screen, (50, 50, 50), (170, 300), 20, 2) # 枠線
            # 右ライトボタン
            pygame.draw.circle(screen, r_color, (630, 300), 20)
            pygame.draw.circle(screen, (50, 50, 50), (630, 300), 20, 2) # 枠線

            # ★修正：3. 遠近感を持たせた敵の描画（ライト点灯時）
            for enemy in self.enemies:
                if self.player.left_light_active:
                    if enemy.position_id == 3: # 部屋3（左の通路：遠く）
                        if not self.player.left_door_closed:
                            scaled_img = pygame.transform.scale(enemy.image, (80, 80))
                            screen.blit(scaled_img, (80, 350)) 
                    elif enemy.position_id == 5: # 部屋5（左扉の前：直前）
                        if not self.player.left_door_closed:
                            scaled_img = pygame.transform.scale(enemy.image, (200, 200))
                            screen.blit(scaled_img, (25, 350))
                            self.SE_hora.play()
                        
                if self.player.right_light_active:
                    if enemy.position_id == 4: # 部屋4（右の通路：遠く）
                        if not self.player.right_door_closed:
                            scaled_img = pygame.transform.scale(enemy.image, (80, 80))
                            screen.blit(scaled_img, (650, 350))
                    elif enemy.position_id == 6: # 部屋6（右扉の前：直前）
                        if not self.player.right_door_closed:
                            scaled_img = pygame.transform.scale(enemy.image, (200, 200))
                            screen.blit(scaled_img, (550, 350))
                            self.SE_hora.play()
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

            display_hour = 12 if self.game_hour == 0 else self.game_hour
            time_str = f"{display_hour} AM"
        
            # 大きめの文字で描画
            time_text = self.font.render(time_str, True, (255, 255, 255))
            display_night = self.level_id.replace("night_", "Night ")
            night_text = self.font.render(display_night, True, (200, 200, 200))

        
            screen.blit(time_text, (700, 20))
            screen.blit(night_text, (675, 50))

            screen.blit(power_text, (20, 20))
            screen.blit(door_text, (20, 70))
            screen.blit(camera_text, (20, 120))
            screen.blit(light_text, (20, 170)) 

            
        