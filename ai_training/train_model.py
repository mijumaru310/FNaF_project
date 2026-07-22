import os
import numpy as np
import tensorflow as tf
from tensorflow import keras

# 特徴量X: [電力, 左扉, 右扉, 現在の部屋(0-6), カメラID(-1-6)]
X = np.random.rand(2000, 5) 
X[:, 0] *= 100 
X[:, 1] = np.random.randint(0, 2, 2000)
X[:, 2] = np.random.randint(0, 2, 2000)
X[:, 3] = np.random.randint(0, 7, 2000)
X[:, 4] = np.random.randint(-1, 7, 2000)

# 正解ラベルy (0: 待機, 1: ルート1(主に後退), 2: ルート2(前進), 3: ルート3(前進))
y = np.zeros(2000, dtype=int)

for i in range(2000):
    power = X[i, 0]
    left = X[i, 1]
    right = X[i, 2]
    pos = int(X[i, 3])
    cam = int(X[i, 4])
    
    # 基本はランダムな行動 (0, 1, 2, 3)
    action = np.random.randint(0, 4)
    
    # ★戦略的ルールベースの組み込み
    if cam == pos:
        # ルール1: カメラで見られている時は「待機(0)」か「後退(1)」を選ぶ
        action = np.random.choice([0])
        
    else:
        # ルール2: 左扉が閉まっているのに左ルート(3, 5)にいる場合は「後退(1)」して別ルートを探す
        if left == 1 and pos in [3, 5]:
            action = 1 
        elif left == 1 and pos in [0, 1]:
            action = 3 
        elif left == 1 and pos in [4,6]:
            action = 2 
        elif left == 1 and pos in [2]:
            action = 1 
            
        # ルール3: 右扉が閉まっているのに右ルート(4, 6)にいる場合は「後退」して別ルートを探す
        elif right == 1 and pos in [4, 6]:
            # 部屋4からの後退は 1(ダイニングへ)か 2(物置へ)。部屋6からの後退は 1(右通路へ)。
            action = 1 
        elif right == 1 and pos in [0, 1]:
            action = 2
        elif right == 1 and pos in [3, 5]:
            action = 2
        elif right == 1 and pos in [2]:
            action = 1
            
        # ルール4: 扉が開いていてカメラも見られていない「隙」は積極的に前進する
        elif cam == -1 and left == 0 and right == 0:
            if pos == 0: action = np.random.choice([2, 3])   # [3, 6] のどちらかへ
            elif pos == 1: action = np.random.choice([2, 3]) # [1, 2] なので前進は 2 か 3
            elif pos == 2: action = 2                        # [2] なので前進は 2
            elif pos == 3: action = 2                        # [3, 4] なので前進は 2
            elif pos == 4: action = 3                        # [3, 5, 6] なので前進は 3
            
    y[i] = action

# モデル構築（出力層を3から4に変更）
model = keras.Sequential([
    keras.layers.Dense(32, activation='relu', input_shape=(5,)),
    keras.layers.Dense(32, activation='relu'),
    keras.layers.Dense(4, activation='softmax') # 4つの行動確率を出力
])

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
# 学習回数を増やしてしっかり覚えさせる
model.fit(X, y, epochs=30) 

os.makedirs('../models', exist_ok=True)
model.save('../models/nn_model.keras')
print("★ 戦略的AIモデルを保存しました！")