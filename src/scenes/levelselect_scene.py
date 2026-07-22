import sys
import pygame
from pygame.locals import *
from src.core.base_scene import BaseScene
# 循環参照を防ぐため、GameSceneとTitleSceneは使用時にインポートします

class LevelSelectScene(BaseScene):
    def __init__(self, manager):
        self.manager = manager
        self.font_title = pygame.font.Font(None, 80)
        self.font_button = pygame.font.Font(None, 50)
        
        # 5つのレベルボタンの当たり判定(Rect)
        self.buttons = {
            "night_1": pygame.Rect(300, 150, 200, 50),
            "night_2": pygame.Rect(300, 220, 200, 50),
            "night_3": pygame.Rect(300, 290, 200, 50),
            "night_4": pygame.Rect(300, 360, 200, 50),
            "night_5": pygame.Rect(300, 430, 200, 50)
        }
        # タイトルに戻るボタン
        self.back_button = pygame.Rect(300, 520, 200, 50)

    def process_event(self, event):
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            # 5つのレベルのどれかがクリックされたら、そのレベルIDを渡してゲーム開始
            for level_id, rect in self.buttons.items():
                if rect.collidepoint(event.pos):
                    from src.scenes.game_scene import GameScene
                    self.manager.change_scene(GameScene(self.manager, level_id=level_id))
            
            # BACKボタンが押されたらタイトルへ戻る
            if self.back_button.collidepoint(event.pos):
                from src.scenes.title_scene import TitleScene
                self.manager.change_scene(TitleScene(self.manager))

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((20, 20, 20))
        
        # タイトルの描画
        title_text = self.font_title.render("Select Level", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(400, 80))
        screen.blit(title_text, title_rect)

        mouse_pos = pygame.mouse.get_pos()
        
        # レベルボタンの描画（ホバーエフェクト付き）
        level_names = {
            "night_1": "Night 1", "night_2": "Night 2", 
            "night_3": "Night 3", "night_4": "Night 4", "night_5": "Night 5"
        }
        for level_id, rect in self.buttons.items():
            color = (100, 100, 100) if rect.collidepoint(mouse_pos) else (50, 50, 50)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (255, 255, 255), rect, 2)
            
            text = self.font_button.render(level_names[level_id], True, (255, 255, 255))
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)

        # BACKボタンの描画
        back_color = (150, 50, 50) if self.back_button.collidepoint(mouse_pos) else (100, 30, 30)
        pygame.draw.rect(screen, back_color, self.back_button)
        pygame.draw.rect(screen, (255, 255, 255), self.back_button, 2)
        back_text = self.font_button.render("BACK", True, (255, 255, 255))
        back_rect = back_text.get_rect(center=self.back_button.center)
        screen.blit(back_text, back_rect)