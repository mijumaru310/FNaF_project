# 抽象クラス(ABC)としてのシーンの土台
from abc import ABC,abstractmethod

class BaseScene(ABC):
    @abstractmethod
    def process_event(self,event):
        """キーボードやマウスクリックなどのイベントを処理します"""
        pass

    @abstractmethod
    def update(self, dt):
        """オブジェクトの状態や時間を更新します（dtはデルタタイム）"""
        pass

    @abstractmethod
    def draw(self, screen):
        """画面への描画処理を行います"""
        pass