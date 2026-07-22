"""
適応型AI (Adaptive AI) の学習スクリプト

プレイヤーの操作パターン（ドア閉鎖率、カメラ使用率等）から
最適な攻撃戦略を予測する RandomForest モデルを学習する。

【特徴量 (7次元)】
  - left_door_rate   : 左ドア閉鎖率 (0.0-1.0)
  - right_door_rate  : 右ドア閉鎖率 (0.0-1.0)
  - camera_rate      : カメラ使用率 (0.0-1.0)
  - left_light_rate  : 左ライト使用率 (0.0-1.0)
  - right_light_rate : 右ライト使用率 (0.0-1.0)
  - power            : 残り電力 (0-100)
  - game_hour        : ゲーム内時刻 (0-5)

【予測ラベル (4クラス)】
  0: ATTACK_LEFT  - 左ルートから攻撃（プレイヤーが右を重点ガード時）
  1: ATTACK_RIGHT - 右ルートから攻撃（プレイヤーが左を重点ガード時）
  2: AGGRESSIVE   - 積極的に前進（プレイヤーの反応が遅い・防御が手薄な時）
  3: CAUTIOUS     - 慎重に行動（プレイヤーがバランス良く防御している時）

【データ生成の考え方】
  実際のプレイヤーの操作データが蓄積される前でも動作するよう、
  多様なプレイスタイルをシミュレートした合成データで事前学習する。
  ゲームプレイ中に蓄積されたログで再学習すれば精度が向上する。
"""

import os
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
import joblib
import pandas as pd

# ===========================================
# 1. 合成データの生成
# ===========================================
np.random.seed(42)
N_SAMPLES = 8000

X = np.zeros((N_SAMPLES, 7))
y = np.zeros(N_SAMPLES, dtype=int)

for i in range(N_SAMPLES):
    # 多様なプレイヤー行動パターンを生成（Beta分布でリアルな偏りを再現）
    left_door = np.random.beta(2, 5)     # ドア閉鎖率は通常低め
    right_door = np.random.beta(2, 5)
    camera = np.random.beta(3, 4)        # カメラ使用率は中程度
    left_light = np.random.beta(1, 8)    # ライト使用率は低め
    right_light = np.random.beta(1, 8)
    power = np.random.uniform(0, 100)    # 電力は0-100の一様分布
    game_hour = np.random.randint(0, 6)  # ゲーム内時刻 0-5

    X[i] = [left_door, right_door, camera, left_light, right_light, power, game_hour]

    # -------------------------------------------
    # ラベリングルール：プレイヤーの防御パターンに基づく最適攻撃戦略
    # -------------------------------------------
    door_diff = left_door - right_door   # 正 = 左をより多くガード
    total_door = left_door + right_door  # 全体のドア使用量
    light_diff = left_light - right_light  # ライトの左右偏り

    # 複合的な左右偏りスコア（ドア + ライトの両方を考慮）
    bias_score = door_diff * 0.7 + light_diff * 0.3

    if bias_score > 0.12:
        # プレイヤーが左を重点的にガード → 右から攻撃
        y[i] = 1  # ATTACK_RIGHT
    elif bias_score < -0.12:
        # プレイヤーが右を重点的にガード → 左から攻撃
        y[i] = 0  # ATTACK_LEFT
    elif camera > 0.5 and total_door < 0.3:
        # カメラ多用 + ドア少 → 反応が遅い → アグレッシブ
        y[i] = 2  # AGGRESSIVE
    elif total_door > 0.5 and camera < 0.2:
        # ドア多用 + カメラ少 → 敵の位置を把握していない → アグレッシブ
        y[i] = 2  # AGGRESSIVE
    else:
        # バランス型 → 慎重に行動
        y[i] = 3  # CAUTIOUS

    # 電力が少ない場合の補正：防御手段が使えなくなるため積極的に攻撃
    if power < 20 and np.random.random() < 0.6:
        y[i] = 2  # AGGRESSIVE

    # 終盤（4-5 AM）の補正：プレイヤーは電力を温存しがち
    if game_hour >= 4 and total_door < 0.2 and np.random.random() < 0.4:
        y[i] = 2  # AGGRESSIVE

# ===========================================
# 1.5 実データの読み込みと追加 (CSVがあれば)
# ===========================================
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, '..')
csv_path = os.path.join(project_root, 'data', 'player_logs.csv')

if os.path.exists(csv_path):
    print(f"\n★ 実際のプレイヤーデータ ({csv_path}) を見つけました。学習に追加します...")
    try:
        df = pd.read_csv(csv_path)
        # CSVの特徴量（7次元）: left_door, right_door, camera, left_light, right_light, power, game_hour
        # ※実データは 0/1 などの離散値ですが、考え方は同じです
        
        # 特徴量の抽出
        # CSVの列名が一致していることを前提
        real_X = df[['left_door', 'right_door', 'camera', 'left_light', 'right_light', 'power', 'game_hour']].values
        real_y = np.zeros(len(real_X), dtype=int)
        
        # 実データに対しても同じラベリングルールを適用
        for i in range(len(real_X)):
            left_door = real_X[i, 0]
            right_door = real_X[i, 1]
            camera = real_X[i, 2]
            left_light = real_X[i, 3]
            right_light = real_X[i, 4]
            power = real_X[i, 5]
            game_hour = real_X[i, 6]
            
            door_diff = left_door - right_door
            total_door = left_door + right_door
            light_diff = left_light - right_light
            bias_score = door_diff * 0.7 + light_diff * 0.3
            
            if bias_score > 0.12:
                real_y[i] = 1
            elif bias_score < -0.12:
                real_y[i] = 0
            elif camera > 0.5 and total_door < 0.3:
                real_y[i] = 2
            elif total_door > 0.5 and camera < 0.2:
                real_y[i] = 2
            else:
                real_y[i] = 3
                
            if power < 20 and np.random.random() < 0.6:
                real_y[i] = 2
            if game_hour >= 4 and total_door < 0.2 and np.random.random() < 0.4:
                real_y[i] = 2
                
        # 合成データと実データを結合
        X = np.vstack((X, real_X))
        y = np.concatenate((y, real_y))
        print(f"  → {len(real_X)} 件の実データを追加しました！")
    except Exception as e:
        print(f"  → CSVの読み込みに失敗しました: {e}")

# ===========================================
# 2. モデルの学習
# ===========================================
print("=" * 60)
print("  適応型AI (Adaptive AI) - プレイヤー行動予測モデルの学習")
print("=" * 60)
print(f"\nデータ数: {N_SAMPLES}サンプル")
print(f"特徴量数: {X.shape[1]}次元")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"訓練データ: {len(X_train)}件 / テストデータ: {len(X_test)}件")

model = RandomForestClassifier(
    n_estimators=150,
    max_depth=12,
    random_state=42
)
model.fit(X_train, y_train)

# ===========================================
# 3. 評価
# ===========================================
y_pred = model.predict(X_test)

print(f"\n正答率 (Accuracy): {accuracy_score(y_test, y_pred):.3f}")

print("\n▼ 混同行列 (Confusion Matrix)")
print("  (行: 正解戦略, 列: AIが予測した戦略)")
print(confusion_matrix(y_test, y_pred))

target_names = ["ATTACK_LEFT", "ATTACK_RIGHT", "AGGRESSIVE", "CAUTIOUS"]
print("\n▼ 詳細レポート (Precision, Recall, F1-score)")
print(classification_report(y_test, y_pred, target_names=target_names, zero_division=0))

# 特徴量重要度の表示
print("▼ 特徴量重要度 (Feature Importances)")
feature_names = [
    "left_door_rate", "right_door_rate", "camera_rate",
    "left_light_rate", "right_light_rate", "power", "game_hour"
]
for name, imp in sorted(
    zip(feature_names, model.feature_importances_),
    key=lambda x: x[1], reverse=True
):
    bar = "#" * int(imp * 50)
    print(f"  {name:>20s}: {imp:.3f} {bar}")

# ===========================================
# 4. モデルの保存
# ===========================================
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(script_dir, '..')
models_dir = os.path.join(project_root, 'models')
os.makedirs(models_dir, exist_ok=True)
save_path = os.path.join(models_dir, 'adaptive_model.pkl')
joblib.dump(model, save_path)
print(f"\n★ 適応型AIモデルを保存しました: {save_path}")
print("  → ゲーム実行時に models/adaptive_model.pkl として読み込まれます")
