import sys
import pygame
from pygame.locals import *
from src.core.base_scene import BaseScene

class GameClearScene(BaseScene):
    def __init__(self, manager):
        self.manager = manager
        self.timer = 0.0
        
        # フォントサイズを大きめに設定
        self.font_large = pygame.font.Font(None, 120)
        self.font_small = pygame.font.Font(None, 60)
        pygame.mixer.Sound("assets/sounds/chaim.mp3").play()
        clearsound_path = "assets/sounds/chaim.mp3"

    def process_event(self, event):
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            pygame.quit()
            sys.exit()

    def update(self, dt):
        self.timer += dt
        # 5秒後に終了する（将来的にタイトル画面に戻るように変更可能です）
        if self.timer > 10.0:
            from src.scenes.levelselect_scene import LevelSelectScene
            self.manager.change_scene(LevelSelectScene(self.manager))

    def draw(self, screen):
        screen.fill((0, 0, 0)) # 背景は真っ黒
        
        # FNaF本家風の「5 AM ... 6 AM」と切り替わる演出
        if self.timer < 2.0:
            time_text = "5 AM"
        else:
            time_text = "6 AM"
            
        text_surface = self.font_large.render(time_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(400, 300))
        screen.blit(text_surface, text_rect)
        
        # 2秒経過したら「You Survived!」の文字を表示
        if self.timer > 4.0:
            cheer_surface = self.font_small.render("You Survived!", True, (200, 200, 200))
            cheer_rect = cheer_surface.get_rect(center=(400, 400))
            screen.blit(cheer_surface, cheer_rect)