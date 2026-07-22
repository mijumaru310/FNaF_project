from tensorflow import keras
import numpy as np
import joblib 

class AIController:
    def __init__(self, model_path="models/rf_model_night_1.pkl"):
        try:
            self.model = joblib.load(model_path)
            print(f"★ AIモデルを読み込みました: {model_path}")
        except Exception as e:
            print(f"AIモデルの読み込みに失敗しました: {e}")
            self.model = None
        
    def predict_action(self, power, left_door, right_door, position_id, camera_id, room_graph):
        x = np.array([[power, float(left_door), float(right_door), float(position_id), float(camera_id)]])
        #predictions = self.model.predict(x)
        #action = np.argmax(predictions)
        action=self.model.predict(x)
        print(f"action:{action}")
        
        possible_moves = room_graph.get(position_id, [])
        
        # 具体的な部屋IDではなく、選択肢の数で行動できるか判定する
        # AIが「ルート1」を選んだが、進める道が0個なら待機(0)
        #if len(possible_moves) == 0:
            #action = 0 
        #elif action == 2 and len(possible_moves) == 1:
            #action = 1 
             
        return action