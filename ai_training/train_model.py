import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
import joblib 

os.makedirs('../models', exist_ok=True)

# Night 1 〜 Night 5 までのモデルを連続で学習して保存する
for night in range(1, 6):
    print(f"--- Night {night} のAIモデルを学習中 ---")
    
    # 特徴量X: [電力, 左扉, 右扉, 現在の部屋(0-6), カメラID(-1-6)]
    X = np.random.rand(6000, 5) 
    X[:, 0] *= 100 
    X[:, 1] = np.random.randint(0, 2, 6000)
    X[:, 2] = np.random.randint(0, 2, 6000)
    X[:, 3] = np.random.randint(0, 7, 6000)
    X[:, 4] = np.random.randint(-1, 7, 6000)

    # 正解ラベルy (0: 待機, 1: ルート1, 2: ルート2, 3: ルート3)
    y = np.zeros(6000, dtype=int)

    for i in range(6000):
        power = X[i, 0]
        left = X[i, 1]
        right = X[i, 2]
        pos = int(X[i, 3])
        cam = int(X[i, 4])
        
        # ★Nightごとの性格付け
        if night == 1:
            # Night 1: チュートリアル。25%の確率で何もしない(待機)
            action = 0 if np.random.rand() < 0.25 else np.random.randint(1, 4)
            
        elif night == 5:
            action = np.random.randint(0, 4)
            # Night 5: 凶悪。フェイントなしで常に最短ルートで猛攻
            if cam == pos:
                action = np.random.choice([0])
            else:
                if left == 1 and pos in [3, 5]: action = 1 
                elif left == 1 and pos in [0,1]: action = 3 
                elif left == 1 and pos in [4, 6]: action = 2 
                elif left == 1 and pos in [2]: action = 1 
                elif right == 1 and pos in [4, 6]: action = 1 
                elif right == 1 and pos in [0,1]: action = 2
                elif right == 1 and pos in [3, 5]: action = 2
                elif right == 1 and pos in [2]: action = 1
                elif cam == -1 and left == 0 and right == 0:
                    if pos == 0: action = np.random.choice([2, 3])   
                    elif pos == 1: action = np.random.choice([2, 3]) 
                    elif pos == 2: action = 2                        
                    elif pos == 3: action = 2                        
                    elif pos == 4: action = 3
                    
                    
        else:
            action = np.random.randint(0, 4)
            # Night 2〜4: ユーザー作成の完璧な経路ルール 
            if cam == pos:
                action = np.random.choice([0])
            else:
                if left == 1 and pos in [3, 5]: action = 1 
                elif left == 1 and pos in [0,1]: action = 3 
                elif left == 1 and pos in [4, 6]: action = 2 
                elif left == 1 and pos in [6]: action = 1 
                elif right == 1 and pos in [4, 6]: action = 1 
                elif right == 1 and pos in [0,1]: action = 2
                elif right == 1 and pos in [3, 5]: action = 2
                elif right == 1 and pos in [2]: action = 1
                elif cam == -1 and left == 0 and right == 0:
                    if pos == 0: action = np.random.choice([2, 3])   
                    elif pos == 1: action = np.random.choice([2, 3]) 
                    elif pos == 2: action = 2                        
                    elif pos == 3: action = 2                        
                    elif pos == 4: action = 3
                    
                        
        y[i] = action
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=0
    )

    model = RandomForestClassifier(n_estimators=200, random_state=0)

    # 2. 学習の実行
    model.fit(X_train, y_train)
    y_pred =model.predict(X_test)
    print("\n[評価指標レポート]")
    print(f"正答率 (Accuracy): {accuracy_score(y_test, y_pred):.3f}")
    
    print("\n▼ 混同行列 (Confusion Matrix)")
    print("(行: 本当の行動, 列: AIが予測した行動)")
    print(confusion_matrix(y_test, y_pred))
    
    print("\n▼ 詳細レポート (Precision, Recall, F1-score)")
    print(classification_report(y_test, y_pred, zero_division=0))


    # 4. モデルの保存（.kerasではなく .pkl 形式などで保存）
    save_path = f'../models/rf_model_night_{night}.pkl'
    joblib.dump(model, save_path)
    print(f"★ {save_path} に保存しました！")