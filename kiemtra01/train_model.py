import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import SimpleRNN, LSTM, Bidirectional, Dense, Embedding
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import matplotlib.pyplot as plt

# 1. Tải và chuẩn bị dữ liệu
print("Đang tải dữ liệu...")
df = pd.read_csv('data_user500.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values(by=['user_id', 'timestamp'])

# Mã hóa action: view=0, click=1, add_to_cart=2
action_map = {'view': 0, 'click': 1, 'add_to_cart': 2}
df['action_code'] = df['action'].map(action_map)

# 2. Xây dựng sequence (chuỗi hành vi)
SEQ_LEN = 4  # Số lượng hành vi để dự đoán hành vi thứ (SEQ_LEN + 1)
X = []
y = []

# Duyệt qua từng user để tạo sequence
for user, group in df.groupby('user_id'):
    actions = group['action_code'].values
    if len(actions) <= SEQ_LEN:
        continue
    for i in range(len(actions) - SEQ_LEN):
        X.append(actions[i:i+SEQ_LEN])
        y.append(actions[i+SEQ_LEN])

X = np.array(X)
y = np.array(y)

print(f"Tổng số tập sequence: {len(X)}")

# Chia tập train/test (80/20)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Định nghĩa các mô hình
def build_model(model_type):
    model = Sequential()
    # input_dim=3 vì có 3 loại action (0,1,2). output_dim=8 làm nhúng nhỏ gọn.
    model.add(Embedding(input_dim=3, output_dim=8, input_length=SEQ_LEN))
    
    if model_type == 'RNN':
        model.add(SimpleRNN(16))
    elif model_type == 'LSTM':
        model.add(LSTM(16))
    elif model_type == 'BiLSTM':
        model.add(Bidirectional(LSTM(16)))
        
    model.add(Dense(3, activation='softmax'))
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

models_dict = {
    'RNN': build_model('RNN'), 
    'LSTM': build_model('LSTM'), 
    'BiLSTM': build_model('BiLSTM')
}

histories = {}
metrics_results = {}

EPOCHS = 15
BATCH_SIZE = 32

print("Bắt đầu huấn luyện và đánh giá...")

# 4. Huấn luyện và đánh giá
for name, model in models_dict.items():
    print(f"[{name}] Đang huấn luyện...")
    history = model.fit(
        X_train, y_train, 
        epochs=EPOCHS, 
        batch_size=BATCH_SIZE, 
        validation_data=(X_test, y_test), 
        verbose=0
    )
    histories[name] = history
    
    # Dự đoán
    y_pred_probs = model.predict(X_test, verbose=0)
    y_pred = np.argmax(y_pred_probs, axis=1)
    
    # Tính toán Metric
    acc = accuracy_score(y_test, y_pred)
    # Dùng weighted vì tập dữ liệu mất cân bằng (view chiếm đa số 70%)
    prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    
    metrics_results[name] = {'Accuracy': acc, 'Precision': prec, 'Recall': rec, 'F1-score': f1}

# 5. Vẽ biểu đồ so sánh
plt.figure(figsize=(14, 10))

# Plot Accuracy
plt.subplot(2, 1, 1)
for name in models_dict.keys():
    plt.plot(histories[name].history['accuracy'], label=f'{name} Train')
    plt.plot(histories[name].history['val_accuracy'], label=f'{name} Val', linestyle='--')
plt.title('Biểu đồ so sánh Accuracy (Train/Test)', fontsize=14)
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend()
plt.grid(True)

# Plot Loss
plt.subplot(2, 1, 2)
for name in models_dict.keys():
    plt.plot(histories[name].history['loss'], label=f'{name} Train')
    plt.plot(histories[name].history['val_loss'], label=f'{name} Val', linestyle='--')
plt.title('Biểu đồ so sánh Loss (Train/Test)', fontsize=14)
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig('model_comparison.png')
print("\n=> Đã lưu biểu đồ vào file 'model_comparison.png'")

# 6. So sánh và kết luận mô hình tốt nhất (dựa trên F1-Score do label mất cân bằng)
best_model_name = max(metrics_results, key=lambda k: metrics_results[k]['F1-score'])

print("\n" + "="*40)
print("KẾT QUẢ ĐÁNH GIÁ (TEST SET):")
print("="*40)
for name, metrics in metrics_results.items():
    print(f"Mô hình: {name}")
    for m_name, m_val in metrics.items():
        print(f"  - {m_name}: {m_val:.4f}")
    print("-" * 25)

print(f"\n[KẾT LUẬN]: {best_model_name} là model_best.")
print(f"Lý do: \n- File mock data có tỉ lệ hành động (view 70%, click 20%, add_to_cart 10%) nên bị mất cân bằng dữ liệu ở các class.")
print(f"- Thay vì chỉ xét Accuracy, việc dựa vào F1-score (Trung bình điều hòa của Precision & Recall) sẽ phản ánh đúng hơn hiệu suất thực tế của mô hình.")
print(f"- {best_model_name} đạt được mức F1-score cao nhất ({metrics_results[best_model_name]['F1-score']:.4f}) trong số các mô hình được thử nghiệm, cho thấy khả năng nhớ được ngữ cảnh chuỗi (tính Sequential) tốt hơn trên tập test phân bố không đều này.")