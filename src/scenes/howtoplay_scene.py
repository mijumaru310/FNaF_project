import sys
import pygame
from pygame.locals import *
from src.core.base_scene import BaseScene

class HowToPlayScene(BaseScene):
    def __init__(self, manager):
        self.manager = manager
        
        # フォントの設定（タイトル用、本文用、ボタン用）
        self.font_title = pygame.font.Font(None, 80)
        self.font_text = pygame.font.Font(None, 25)
        self.font_button = pygame.font.Font(None, 50)
        
        # タイトルに戻るボタン
        self.back_button = pygame.Rect(300, 500, 200, 50)
        
        # 画面に表示する説明文（英語でFNaFの雰囲気を出しつつわかりやすく）
        self.instructions = [
            "This is Nagoya University at night.",
            "You play the role of a security guard and monitor the campus.",
            "GOAL: Survive until 6 AM.",
            "Do not let the Monsters enter your room.",
            "",
            "[SPACE]: Open / Close Camera Monitor",
            "  * Click the bottom-right map to switch cameras.",
            "[A] / [D] or Click UI:: Close Left / Right Door",
            "[Q] / [E] or Click UI: Turn on Left / Right Light",
            "WARNING: Using doors, lights, and cameras consumes POWER.",
            "If POWER reaches 0%, the system will shut down..."
        ]

    def process_event(self, event):
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            # BACKボタンが押されたらタイトルへ戻る
            if self.back_button.collidepoint(event.pos):
                from src.scenes.title_scene import TitleScene
                self.manager.change_scene(TitleScene(self.manager))

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((20, 20, 30)) # 少し青みがかった暗い背景
        
        # タイトルの描画
        title_text = self.font_title.render("HOW TO PLAY", True, (255, 255, 100))
        title_rect = title_text.get_rect(center=(400, 60))
        screen.blit(title_text, title_rect)

        # 説明文の描画（1行ずつずらして表示）
        start_y = 130
        for i, line in enumerate(self.instructions):
            if "WARNING" in line or "0%" in line:
                color = (255, 100, 100) # 警告文は赤っぽく
            else:
                color = (200, 200, 200) # 通常文は白っぽく
                
            text_surface = self.font_text.render(line, True, color)
            # 左揃えで描画
            screen.blit(text_surface, (50, start_y + i * 35))

        # BACKボタンの描画
        mouse_pos = pygame.mouse.get_pos()
        back_color = (150, 50, 50) if self.back_button.collidepoint(mouse_pos) else (100, 30, 30)
        
        pygame.draw.rect(screen, back_color, self.back_button)
        pygame.draw.rect(screen, (255, 255, 255), self.back_button, 2)
        back_text = self.font_button.render("BACK", True, (255, 255, 255))
        back_rect = back_text.get_rect(center=self.back_button.center)
        screen.blit(back_text, back_rect)