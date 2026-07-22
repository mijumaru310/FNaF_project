import sys
import pygame
import cv2
import numpy as np
from pygame.locals import *
from src.core.base_scene import BaseScene

class GameOverScene(BaseScene):
    def __init__(self, manager):
        self.manager = manager
        self.font = pygame.font.SysFont(None, 100)
        self.timer = 0.0
        video_path = "assets/movie/fredy_attack.mp4" 
        self.cap = cv2.VideoCapture(video_path)
        
        if not self.cap.isOpened():
            print(f"エラー：動画が見つかりません。パスを確認してください -> {video_path}")

        # 音声も鳴らす場合はここで効果音を読み込んで再生します
        pygame.mixer.Sound("assets/sounds/death_sound.mp3").play()

    def process_event(self, event):
        # 演出中はキーボード入力を受け付けないようにするか、ESCで終了させる
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            self.cap.release()
            pygame.quit()
            sys.exit()

    def update(self, dt):
        pass
        #self.timer += dt
        # 3秒経過したら強制終了（後でタイトル画面に戻す処理に変更できます）
        #if self.timer > 3.0:
            #pygame.quit()
            #sys.exit()

    def draw(self, screen):

        screen.fill((0, 0, 0))
        if self.cap.isOpened():
            # 動画から1フレーム（1コマ）読み込む
            ret, frame = self.cap.read()
            
            if ret:
                # 1. OpenCVの画像データ(BGR配列)を、Pygame用(RGB配列)に色変換
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # 2. Pygameの画面サイズ（例: 800x600）に合わせてリサイズ
                # ※ご自身の main.py の画面サイズ設定に合わせて数値を変更してください
                frame_resized = cv2.resize(frame_rgb, (800, 600))
                
                # 3. OpenCVの配列(縦x横)を、PygameのSurface(横x縦)に変換
                frame_surface = pygame.surfarray.make_surface(frame_resized.swapaxes(0, 1))
                
                # 4. 画面に描画
                screen.blit(frame_surface, (0, 0))
            else:
                # 動画が最後まで再生された（ret == False）らゲーム終了
                self.cap.release()
                from src.scenes.title_scene import TitleScene
                self.manager.change_scene(TitleScene(self.manager))
        else:
            # 動画が読み込めなかった場合の予備画面（真っ暗）
            # 画面を赤く染めて恐怖演出のベースにする
            screen.fill((150, 0, 0))
            # 画面中央にGAME OVERの文字を配置
            text = self.font.render("GAME OVER", True, (0, 0, 0))
            text_rect = text.get_rect(center=(400, 300)) 
            screen.blit(text, text_rect)

        