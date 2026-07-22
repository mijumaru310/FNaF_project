import tensorflow as tf
import numpy as np

class AIController:
    def __init__(self, model_path):
        # 授業で学んだ「学習済みモデルの読み込み」
        self.model = tf.keras.models.load_model(model_path)
        
    def predict_action(self, power, left_door, right_door, position_id, camera_id, room_graph):
        x = np.array([[power, float(left_door), float(right_door), float(position_id), float(camera_id)]])
        predictions = self.model.predict(x, verbose=0)
        action = np.argmax(predictions)
        print(f"action:{action}")
        
        possible_moves = room_graph.get(position_id, [])
        
        # 具体的な部屋IDではなく、選択肢の数で行動できるか判定する
        # AIが「ルート1」を選んだが、進める道が0個なら待機(0)
        #if len(possible_moves) == 0:
            #action = 0 
        #elif action == 2 and len(possible_moves) == 1:
            #action = 1 
             
        return action