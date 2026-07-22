# シーン管理（Stateパターン）
class SceneManager:
    """
    現在のシーンを管理し、切り替えや処理の橋渡しを行うクラスです。
    """
    def __init__(self, initial_scene):
        # 起動時の最初のシーンをセット
        self.current_scene = initial_scene

    def change_scene(self, next_scene):
        # シーンを切り替える
        self.current_scene = next_scene

    def process_event(self, event):
        # 現在のシーンにイベント処理を任せる
        self.current_scene.process_event(event)

    def update(self, dt):
        # 現在のシーンに更新処理を任せる
        self.current_scene.update(dt)

    def draw(self, screen):
        # 現在のシーンに描画処理を任せる
        self.current_scene.draw(screen)