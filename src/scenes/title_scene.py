import sys
import pygame
from pygame.locals import *
from src.core.base_scene import BaseScene
from src.scenes.levelselect_scene import LevelSelectScene

class TitleScene(BaseScene):
    def __init__(self, manager):
        self.manager = manager
        pygame.mixer.init()
        
        # フォントの設定
        self.font_title = pygame.font.Font(None, 100)
        self.font_button = pygame.font.Font(None, 50)
        
        # ★ボタンの当たり判定(Rect)を画面中央に設定
        self.play_button = pygame.Rect(225, 330, 350, 40)
        self.how_to_button = pygame.Rect(225, 390, 350, 40) # 追加
        self.quit_button = pygame.Rect(225, 450, 350, 40)

        self.bg_image = pygame.image.load("assets/images/title.png").convert()
            # 画面サイズ(例：800x600)に合わせて拡大縮小
        self.bg_image = pygame.transform.scale(self.bg_image, (800, 600))
        pygame.mixer.music.load("assets/sounds/Midnight_Security_Feed.mp3")
        pygame.mixer.music.play(-1)
        

    def process_event(self, event):
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
            
        # ★マウスクリック判定
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.play_button.collidepoint(event.pos):
                # PLAYボタンが押されたらゲーム本編(GameScene)へシーンを切り替える
                pygame.mixer.music.stop()
                self.manager.change_scene(LevelSelectScene(self.manager))
            elif self.how_to_button.collidepoint(event.pos):
                from src.scenes.howtoplay_scene import HowToPlayScene
                self.manager.change_scene(HowToPlayScene(self.manager))
            elif self.quit_button.collidepoint(event.pos):
                # QUITボタンが押されたらゲームを終了する
                pygame.mixer.music.stop()
                pygame.quit()
                sys.exit()

    def update(self, dt):
        pass # タイトル画面では時間経過で更新する処理は特にないのでpass

    def draw(self, screen):
        screen.fill((10, 10, 10)) # 薄暗い背景
        screen.blit(self.bg_image, (0, 0))

        # 1. タイトル文字の描画（名前は自由に変更してください）
        title_text = self.font_title.render("Five Night at Nu", True, (255, 50, 50))
        title_rect = title_text.get_rect(center=(400, 150))
        screen.blit(title_text, title_rect)

        # 2. PLAYボタンの描画
        # マウスがボタンの上にある時は色を明るくする（ホバーエフェクト）
        mouse_pos = pygame.mouse.get_pos()
        play_color = (100, 100, 100) if self.play_button.collidepoint(mouse_pos) else (50, 50, 50)
        
        pygame.draw.rect(screen, play_color, self.play_button)
        pygame.draw.rect(screen, (255, 255, 255), self.play_button, 2) # 枠線
        play_text = self.font_button.render("PLAY", True, (255, 255, 255))
        play_rect = play_text.get_rect(center=self.play_button.center)
        screen.blit(play_text, play_rect)

        # HOW TO PLAYボタン
        howto_color = (100, 100, 100) if self.how_to_button.collidepoint(mouse_pos) else (50, 50, 50)
        pygame.draw.rect(screen, howto_color, self.how_to_button)
        pygame.draw.rect(screen, (255, 255, 255), self.how_to_button, 2) 
        howto_text = self.font_button.render("HOW TO PLAY", True, (255, 255, 255))
        howto_rect = howto_text.get_rect(center=self.how_to_button.center)
        screen.blit(howto_text, howto_rect)

        # 3. QUITボタンの描画
        quit_color = (100, 100, 100) if self.quit_button.collidepoint(mouse_pos) else (50, 50, 50)
        
        pygame.draw.rect(screen, quit_color, self.quit_button)
        pygame.draw.rect(screen, (255, 255, 255), self.quit_button, 2) # 枠線
        quit_text = self.font_button.render("QUIT", True, (255, 255, 255))
        quit_rect = quit_text.get_rect(center=self.quit_button.center)
        screen.blit(quit_text, quit_rect)