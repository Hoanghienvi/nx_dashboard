import os
import subprocess
import sys

def run():
    print("========================================")
    print("   NX REPORT V4 - STABLE VERSION 13     ")
    print("========================================")
    
    # Xác định đường dẫn đến file main.py trong thư mục app
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(base_dir, 'app', 'main.py')
    
    if not os.path.exists(app_path):
        print(f"LỖI: Không tìm thấy file {app_path}")
        return

    # Khởi chạy ứng dụng
    try:
        subprocess.run([sys.executable, app_path])
    except KeyboardInterrupt:
        print("\nĐang đóng ứng dụng...")

if __name__ == '__main__':
    run()