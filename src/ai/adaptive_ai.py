import numpy as np
import joblib
import random

# 攻撃戦略の定数
ATTACK_LEFT = 0   # 左ルートを優先して攻撃
ATTACK_RIGHT = 1  # 右ルートを優先して攻撃
AGGRESSIVE = 2    # 待機を減らし積極的に前進
CAUTIOUS = 3      # 通常行動（既存AIのまま）

STRATEGY_NAMES = {
    ATTACK_LEFT: "ATTACK_LEFT",
    ATTACK_RIGHT: "ATTACK_RIGHT",
    AGGRESSIVE: "AGGRESSIVE",
    CAUTIOUS: "CAUTIOUS"
}


class AdaptiveAI:
    """
    プレイヤーの行動パターンを分析し、弱点を突く攻撃戦略を選択する適応型AI。

    PlayerTracker から受け取った特徴量（ドア閉鎖率・カメラ使用率等）を
    RandomForest モデルに入力し、最適な攻撃方向を予測する。
    """

    def __init__(self, model_path="models/adaptive_model.pkl"):
        """
        Args:
            model_path: 学習済み適応型モデルのファイルパス
        """
        self.model = None
        self.current_strategy = CAUTIOUS
        self.strategy_timer = 0.0
        self.strategy_interval = 5.0  # 5秒ごとに戦略を再評価

        try:
            self.model = joblib.load(model_path)
            print(f"★ 適応型AIモデルを読み込みました: {model_path}")
        except Exception as e:
            print(f"適応型AIモデルの読み込みに失敗: {e}")
            print("  → デフォルト戦略(CAUTIOUS)で動作します")

    def predict_strategy(self, features):
        """
        プレイヤーの行動特徴量から最適な攻撃戦略を予測する。

        Args:
            features: PlayerTracker.get_features() の戻り値

        Returns:
            int: 攻撃戦略ID (ATTACK_LEFT=0, ATTACK_RIGHT=1, AGGRESSIVE=2, CAUTIOUS=3)
        """
        if self.model is None:
            return CAUTIOUS

        x = np.array([[
            features['left_door_rate'],
            features['right_door_rate'],
            features['camera_rate'],
            features['left_light_rate'],
            features['right_light_rate'],
            features['power'],
            features['game_hour']
        ]])

        strategy = self.model.predict(x)[0]
        return int(strategy)

    def update(self, features, dt):
        """
        定期的に攻撃戦略を再評価する。毎フレーム呼び出される。

        Args:
            features: PlayerTracker.get_features() の戻り値
            dt: デルタタイム（秒）
        """
        self.strategy_timer += dt
        if self.strategy_timer >= self.strategy_interval:
            self.strategy_timer = 0.0
            old_strategy = self.current_strategy
            self.current_strategy = self.predict_strategy(features)
            if old_strategy != self.current_strategy:
                print(f"★ AI戦略変更: {STRATEGY_NAMES[old_strategy]} → {STRATEGY_NAMES[self.current_strategy]}")

    def get_strategy_name(self):
        """現在の戦略名を返す"""
        return STRATEGY_NAMES.get(self.current_strategy, "UNKNOWN")

    def apply_bias(self, action, position_id, room_graph):
        """
        既存AIが決定した基本アクションに、戦略に基づくバイアスを適用する。

        プレイヤーの弱点に合わせて、敵の移動先を調整する。
        - ATTACK_LEFT: 分岐点で左ルート(3→5)を選ぶ確率を上げる
        - ATTACK_RIGHT: 分岐点で右ルート(4→6)を選ぶ確率を上げる
        - AGGRESSIVE: 待機(action=0)を前進に変更する確率を上げる
        - CAUTIOUS: バイアスなし（元のアクションをそのまま返す）

        Args:
            action: 既存AIが決定した基本アクション (0=待機, 1=後退, 2=前進1, 3=前進2)
            position_id: 敵の現在の部屋ID
            room_graph: 部屋の接続グラフ

        Returns:
            int: バイアス適用後のアクション
        """
        possible = room_graph.get(position_id, [])
        if len(possible) == 0:
            return action

        if self.current_strategy == ATTACK_LEFT:
            # 左ルートを優先: 分岐点で左方向への移動確率を上げる
            if position_id == 0:  # 奥の部屋 → ダイニング(1)経由で左ルートへ
                if action == 0 and random.random() < 0.6:
                    return 2  # 前進（ダイニングへ）
            elif position_id == 1:  # ダイニング → 左通路(3)を優先
                if random.random() < 0.7:
                    return 2  # ルート2（左通路へ）
            elif position_id == 3:  # 左通路 → 左扉前(5)へ前進
                if action == 0 and random.random() < 0.5:
                    return 2

        elif self.current_strategy == ATTACK_RIGHT:
            # 右ルートを優先: 分岐点で右方向への移動確率を上げる
            if position_id == 0:  # 奥の部屋 → 物置(2)経由で右ルートへ
                if action == 0 and random.random() < 0.6:
                    return 3  # 前進（物置方面へ）
            elif position_id == 1:  # ダイニング → 右通路(4)を優先
                if random.random() < 0.7:
                    return 3  # ルート3（右通路へ）
            elif position_id == 2:  # 物置 → 右通路(4)へ前進
                if action == 0 and random.random() < 0.5:
                    return 2
            elif position_id == 4:  # 右通路 → 右扉前(6)へ前進
                if action == 0 and random.random() < 0.5:
                    return 2

        elif self.current_strategy == AGGRESSIVE:
            # 積極的に前進: 待機を前進に変更
            if action == 0 and random.random() < 0.7:
                if len(possible) > 1:
                    return random.choice([2, 3])
                elif len(possible) > 0:
                    return 2

        # CAUTIOUS の場合、または確率判定に外れた場合は元のアクションを返す
        return action
