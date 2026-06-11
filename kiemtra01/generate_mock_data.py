import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Cài đặt cố định seed để kết quả sinh ngẫu nhiên có thể tái lập
np.random.seed(42)

# Cấu hình dữ liệu
NUM_USERS = 500
MIN_ACTIONS_PER_USER = 8
MAX_ACTIONS_PER_USER = 25
ACTIONS = ['view', 'click', 'add_to_cart']
# Xác suất thực hiện các hành động: view (70%), click (20%), add_to_cart (10%)
ACTION_PROBS = [0.7, 0.2, 0.1]
NUM_PRODUCTS = 100

data = []

# Chọn một thời điểm bắt đầu gốc
base_start_time = datetime(2023, 1, 1, 8, 0, 0)

for user_num in range(1, NUM_USERS + 1):
    user_id = f"user_{user_num:03d}"
    
    # Số lượng hành vi tối thiểu là 8, tối đa là ngẫu nhiên
    num_behaviors = np.random.randint(MIN_ACTIONS_PER_USER, MAX_ACTIONS_PER_USER + 1)
    
    # Mỗi user sẽ bắt đầu phiên (session) trong một khoảng thời gian ngẫu nhiên so với gốc
    current_time = base_start_time + timedelta(
        days=np.random.randint(0, 30), 
        hours=np.random.randint(0, 24),
        minutes=np.random.randint(0, 60)
    )
    
    for _ in range(num_behaviors):
        product_id = f"P{np.random.randint(1, NUM_PRODUCTS + 1):03d}"
        action = np.random.choice(ACTIONS, p=ACTION_PROBS)
        
        data.append({
            'user_id': user_id,
            'product_id': product_id,
            'action': action,
            'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S')
        })
        
        # Đảm bảo tính logic: timestamp của hành động tiếp theo phải tăng lên (từ 5 giây đến 10 phút)
        time_increment = timedelta(seconds=np.random.randint(5, 600))
        current_time += time_increment

# Tạo DataFrame
df = pd.DataFrame(data)

# Xuất ra file
output_file = 'data_user500.csv'
df.to_csv(output_file, index=False)

print(f"Đã tạo thành công file '{output_file}' với {len(df)} dòng dữ liệu giả lập.")
print(df.head(15))
