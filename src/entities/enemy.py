import pygame
import random

class BaseEnemy(pygame.sprite.Sprite):
    """すべての敵の親となる基本クラス"""
    def __init__(self, player, name, image_path, interval, ai_controller=None):
        super().__init__()
        try:
            raw_image = pygame.image.load(image_path).convert_alpha()
            # 50x50サイズに調整（画像の元のサイズに合わせて変更可能）
            self.image = pygame.transform.scale(raw_image, (50, 50))
        except FileNotFoundError:
            # 画像が見つからない場合のエラー回避用（今まで通りの四角形）
            print(f"画像が見つかりません: {image_path}")
            self.image = pygame.Surface((50, 50))
            self.image.fill((255, 0, 0))
            
        self.rect = self.image.get_rect()
        
        self.player = player
        self.name = name 
        self.position_id = 0
        self.move_timer = 0.0
        self.move_interval = interval 
        self.ai_controller = ai_controller
        self.is_attacking = False 
        
        # ユーザーが設定したルーム番号とつながりをそのまま使用
        self.room_graph = {
            0: [0,1, 2],    # 奥の部屋からはダイニング(1)か物置(2)へ
            1: [0,3, 4],    # ダイニングからは左通路(3)か右通路(4)へ
            2: [0,4,4],       # 物置からは右通路(4)へ合流してくる
            3: [1,5,5],       # 左通路からは左扉前(5)へ
            4: [random.choice([1,2]),6,6],       # 右通路からは右扉前(6)へ  #エラーでるかも
            5: [3,5,5],       # 左扉前からは戻る(3)のみ
            6: [4,6,6]        # 右扉前からは戻る(4)のみ
        }
        self.update_rect_position()

    def update_rect_position(self):
        positions = [
            (400, 50),  # 0: 奥の部屋
            (400, 150), # 1: ダイニング
            (600, 100), # 2: 物置
            (200, 250), # 3: 左通路
            (600, 250), # 4: 右通路
            (200, 400), # 5: 左扉の前
            (600, 400), # 6: 右扉の前
        ]
        if self.position_id < len(positions):
            self.rect.center = positions[self.position_id]

    def update(self, dt):
        if self.player.camera_active and self.player.current_camera_id == self.position_id:
            return 
        self.move_timer += dt
        if self.move_timer >= self.move_interval:
            self.move_timer = 0.0
            self.move()

    def move(self):
        if self.position_id == 5: 
            if self.player.left_door_closed:
                print(f"{self.name}を左扉で防衛成功！")
                self.on_defended() # 敵の性格によって逃げ方が変わる
            else:
                print(f"{self.name}に左から侵入されました！")
                self.is_attacking = True 
            self.update_rect_position()
            return
            
        elif self.position_id == 6: 
            if self.player.right_door_closed:
                print(f"{self.name}を右扉で防衛成功！")
                self.on_defended() # 敵の性格によって逃げ方が変わる
            else:
                print(f"{self.name}に右から侵入されました！")
                self.is_attacking = True
            self.update_rect_position()
            return

        self.decide_next_room()

    def on_defended(self):
        """防衛された時の処理（ユーザーが作成したロジック）"""
        randlist = [0,1,2,4]
        self.position_id = random.choice(randlist)

    def decide_next_room(self):
        cam_id = self.player.current_camera_id if self.player.camera_active else -1
        if self.ai_controller:
            action = self.ai_controller.predict_action(
                self.player.power, self.player.left_door_closed, self.player.right_door_closed,
                self.position_id, cam_id, self.room_graph
            )
            possible = self.room_graph.get(self.position_id, [])
            
            # アクションに応じてグラフのリストから次の部屋を選ぶ
            # 正解ラベルy (0: 待機, 1: ルート1(主に後退), 2: ルート2(前進), 3: ルート3(前進))
            if action == 1 and len(possible) > 0:
                self.position_id = possible[0] 
            elif action == 2 and len(possible) > 1:
                self.position_id = possible[1]
            elif action == 3 and len(possible) > 1:
                self.position_id = possible[2]
                
        self.update_rect_position()


# ==========================================
# クラスの継承を使った複数の敵の定義
# ==========================================

class StandardEnemy(BaseEnemy):
    """【特徴】赤い。防衛されるとユーザー指定の randlist の部屋に逃げる。"""
    def __init__(self, player, ai_controller):
        super().__init__(player, name="Red(Standard)", image_path="assets/images/Fredy_stand.png", interval=3.0, ai_controller=ai_controller)

class FastEnemy(BaseEnemy):
    """【特徴】青い。移動が速いが、防衛されると必ず初期位置に逃げる。"""
    def __init__(self, player, ai_controller):
        super().__init__(player, name="Blue(Fast)",  image_path="assets/images/Fredy_stand.png", interval=2.0, ai_controller=ai_controller)
    
    def on_defended(self):
        """親クラスの処理をオーバーライド（ポリモーフィズム）"""
        self.position_id = 0