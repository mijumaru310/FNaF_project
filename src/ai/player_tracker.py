import csv
import os


class PlayerTracker:
    """
    プレイヤーの操作をリアルタイムで記録し、行動パターンの特徴量を算出するクラス。
    
    直近 window_size 秒のスライディングウィンドウで行動を集計し、
    適応型AIが攻撃戦略を決定するための特徴量を提供する。
    """

    def __init__(self, window_size=30.0, record_interval=0.5):
        """
        Args:
            window_size: 特徴量計算に使用する直近の秒数（デフォルト30秒）
            record_interval: スナップショット記録の間隔（秒）
        """
        self.window_size = window_size
        self.record_interval = record_interval
        self.snapshots = []
        self.all_snapshots = []  # ログ保存用の全履歴
        self.elapsed_time = 0.0
        self.record_timer = 0.0

    def record(self, player, game_hour, dt):
        """
        毎フレーム呼び出される記録メソッド。
        record_interval ごとにプレイヤーの状態をスナップショットとして保存する。

        Args:
            player: Player オブジェクト
            game_hour: 現在のゲーム内時刻 (0-5)
            dt: デルタタイム（秒）
        """
        self.elapsed_time += dt
        self.record_timer += dt

        if self.record_timer >= self.record_interval:
            self.record_timer = 0.0
            snapshot = {
                'time': round(self.elapsed_time, 2),
                'left_door': int(player.left_door_closed),
                'right_door': int(player.right_door_closed),
                'camera': int(player.camera_active),
                'left_light': int(player.left_light_active),
                'right_light': int(player.right_light_active),
                'power': round(player.power, 1),
                'game_hour': game_hour
            }
            self.snapshots.append(snapshot)
            self.all_snapshots.append(snapshot)

            # スライディングウィンドウ: 古いデータを削除
            cutoff = self.elapsed_time - self.window_size
            self.snapshots = [s for s in self.snapshots if s['time'] >= cutoff]

    def get_features(self):
        """
        直近 window_size 秒のスナップショットからプレイヤー行動の特徴量を計算する。

        Returns:
            dict: 以下のキーを持つ特徴量辞書
                - left_door_rate: 左ドア閉鎖率 (0.0-1.0)
                - right_door_rate: 右ドア閉鎖率 (0.0-1.0)
                - camera_rate: カメラ使用率 (0.0-1.0)
                - left_light_rate: 左ライト使用率 (0.0-1.0)
                - right_light_rate: 右ライト使用率 (0.0-1.0)
                - power: 現在の電力 (0-100)
                - game_hour: 現在のゲーム内時刻 (0-5)
        """
        if len(self.snapshots) < 2:
            # データ不足時はバランス型のデフォルト値を返す
            return {
                'left_door_rate': 0.5,
                'right_door_rate': 0.5,
                'camera_rate': 0.5,
                'left_light_rate': 0.1,
                'right_light_rate': 0.1,
                'power': 100.0,
                'game_hour': 0
            }

        n = len(self.snapshots)
        return {
            'left_door_rate': sum(s['left_door'] for s in self.snapshots) / n,
            'right_door_rate': sum(s['right_door'] for s in self.snapshots) / n,
            'camera_rate': sum(s['camera'] for s in self.snapshots) / n,
            'left_light_rate': sum(s['left_light'] for s in self.snapshots) / n,
            'right_light_rate': sum(s['right_light'] for s in self.snapshots) / n,
            'power': self.snapshots[-1]['power'],
            'game_hour': self.snapshots[-1]['game_hour']
        }

    def save_log(self, filepath="data/player_logs.csv"):
        """
        全セッションのスナップショットをCSVファイルに追記保存する。
        保存されたデータは次回の適応型AI学習に使用できる。

        Args:
            filepath: 保存先CSVファイルパス
        """
        if not self.all_snapshots:
            return

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file_exists = os.path.exists(filepath)

        fieldnames = ['time', 'left_door', 'right_door', 'camera',
                      'left_light', 'right_light', 'power', 'game_hour']
        with open(filepath, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            for snapshot in self.all_snapshots:
                writer.writerow(snapshot)
        
        print(f"★ プレイヤー行動ログを保存しました: {filepath} ({len(self.all_snapshots)}件)")
