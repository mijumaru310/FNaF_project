class Player:
    def __init__(self, decrease_rate=2.0):
        #電力(0-100%)
        self.__power=100.0
        self.left_door_closed = False
        self.right_door_closed = False
        self.camera_active = False
        self.current_camera_id = 1
        self.left_light_active = False
        self.right_light_active = False
        self.decrease_rate = decrease_rate 

    @property
    def power(self):
        """現在の電力を取得するプロパティ"""
        return self.__power

    def consume_power(self, amount):
        """電力を消費し、0未満にならないようにする"""
        self.__power -= amount
        if self.__power < 0:
            self.__power = 0

    def update(self, dt):
        """
        毎フレーム呼ばれる更新処理。
        扉を閉めている、またはカメラを見ていると電力を消費します。
        """
        usage = 0
        if self.left_door_closed: usage += 1
        if self.right_door_closed: usage += 1
        if self.camera_active: usage += 1

        if self.left_light_active: usage += 1
        if self.right_light_active: usage += 1
        # 施設の使用数に応じて電力を消費 (dtを使ってPC性能による差をなくす)
        if usage > 0:
            # 例: 1つ使用につき、1秒間で{self.decrease_rate}%消費
            self.consume_power(usage * self.decrease_rate * dt)