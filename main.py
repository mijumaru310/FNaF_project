import sys
import pygame
from pygame.locals import *
from src.core.scene_manager import SceneManager 
from src.scenes.title_scene import TitleScene 

SCREEN_SIZE = (800, 600)

def main():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption("System Breach / AI Anomaly")

    clock = pygame.time.Clock()
    
    # 最初のシーンをTitleSceneとして初期化し、マネージャーに渡す
    initial_scene = TitleScene(manager=None) 
    manager = SceneManager(initial_scene)
    initial_scene.manager = manager # 相互参照

    while True:
        # PC性能に左右されないよう、デルタタイム（dt）を取得 [2]
        dt = clock.tick(60) / 1000

        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            # マネージャー経由でイベント処理を委譲 [4]
            manager.process_event(event)

        # マネージャー経由で更新と描画を委譲
        manager.update(dt)
        manager.draw(screen)

        pygame.display.flip()

if __name__ == "__main__":
    main()