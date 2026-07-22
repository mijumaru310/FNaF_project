import sys
import pygame
from pygame.locals import *
from src.core.base_scene import BaseScene

class GameOverScene(BaseScene):
    def __init__(self, manager):
        self.manager = manager
        self.font = pygame.font.SysFont(None, 100)
        self.timer = 0.0

    def process_event(self, event):
        # 演出中はキーボード入力を受け付けないようにするか、ESCで終了させる
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            pygame.quit()
            sys.exit()

    def update(self, dt):
        self.timer += dt
        # 3秒経過したら強制終了（後でタイトル画面に戻す処理に変更できます）
        if self.timer > 3.0:
            pygame.quit()
            sys.exit()

    def draw(self, screen):
        # 画面を赤く染めて恐怖演出のベースにする
        screen.fill((150, 0, 0))
        # 画面中央にGAME OVERの文字を配置
        text = self.font.render("GAME OVER", True, (0, 0, 0))
        text_rect = text.get_rect(center=(400, 300)) 
        screen.blit(text, text_rect)