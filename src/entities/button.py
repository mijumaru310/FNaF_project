import pygame
class Button(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height,text,font ):
        super().__init__()
        self.image =pygame.Surface((width,height))
        self.image.fill((100,100,100))

        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        text_surf = font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.image.get_rect().center)
        self.image.blit(text_surf, text_rect)
    def is_clicked(self, mouse_pos):
        """
        クリックとRectの衝突判定 [2]
        マウスの座標(mouse_pos)が、ボタンのRectの中にあるかを返します
        """
        return self.rect.collidepoint(mouse_pos)
