import requests
import json
import urllib3
import os

# Tắt cảnh báo chứng chỉ SSL (cho HTTPS IP nội bộ)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_debug_data():
    print("==================================================")
    print("   TOOL THU THẬP DỮ LIỆU DEBUG NX WITNESS         ")
    print("==================================================")
    
    server = input("1. Nhập URL Server (VD: https://192.168.1.10:7001): ").strip().rstrip('/')
    user = input("2. Nhập Username (admin): ").strip()
    password = input("3. Nhập Password: ").strip()

    if not server.startswith('http'):
        server = 'https://' + server

    session = requests.Session()
    session.verify = False # Bỏ qua check SSL

    # --- 1. ĐĂNG NHẬP ---
    print(f"\n[1/4] Đang kết nối tới {server}...")
    try:
        # Thử Login kiểu cũ (API)
        login_res = session.post(f'{server}/api/login', json={'username': user, 'password': password}, timeout=10)
        
        # Nếu thất bại, thử Login kiểu mới (REST)
        if login_res.status_code != 200:
            login_res = session.post(f'{server}/rest/v1/login/sessions', json={'username': user, 'password': password}, timeout=10)
            if login_res.status_code == 200:
                token = login_res.json().get('token')
                session.headers.update({'Authorization': f'Bearer {token}'})

        if login_res.status_code != 200:
            print(f"❌ Lỗi đăng nhập! Status Code: {login_res.status_code}")
            print("Nội dung lỗi:", login_res.text)
            return
    except Exception as e:
        print(f"❌ Lỗi kết nối: {str(e)}")
        return

    print("✅ Đăng nhập thành công! Đang tải dữ liệu...")
    
    final_data = {
        "server_url": server,
        "collection_time": str(os.times()),
        "devices": [],
        "servers_info": []
    }

    # --- 2. LẤY DỮ LIỆU API REST (REST V3/V4) ---
    # Đây là API mà code hiện tại đang dùng
    try:
        print("[2/4] Đang lấy dữ liệu Devices (REST API)...")
        res = session.get(f'{server}/rest/v3/devices')
        if res.status_code == 200:
            final_data['rest_devices'] = res.json()
        else:
            # Thử v4 nếu v3 không có
            res = session.get(f'{server}/rest/v4/devices')
            final_data['rest_devices'] = res.json() if res.status_code == 200 else f"Error: {res.status_code}"
    except Exception as e:
        final_data['rest_devices_error'] = str(e)

    # --- 3. LẤY DỮ LIỆU API EC2 (Legacy/Detailed) ---
    # API này chứa thông tin rất chi tiết về params, bitrate, storage mà REST đôi khi bị thiếu
    try:
        print("[3/4] Đang lấy dữ liệu CamerasEx (EC2 API)...")
        res = session.get(f'{server}/ec2/getCamerasEx')
        if res.status_code == 200:
            final_data['ec2_cameras'] = res.json()
    except Exception as e:
        final_data['ec2_cameras_error'] = str(e)

    # --- 4. LẤY DỮ LIỆU SERVER STATS (Storage tổng) ---
    try:
        print("[4/4] Đang lấy dữ liệu Media Servers...")
        res = session.get(f'{server}/ec2/getMediaServers')
        if res.status_code == 200:
            final_data['media_servers'] = res.json()
    except Exception as e:
        final_data['media_servers_error'] = str(e)

    # --- XUẤT FILE ---
    filename = "nx_debug_data.json"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=4, ensure_ascii=False)
        print("\n==================================================")
        print(f"✅ ĐÃ XUẤT FILE THÀNH CÔNG: {filename}")
        print("👉 Vui lòng upload file này lên khung chat để tôi phân tích.")
        print("==================================================")
    except Exception as e:
        print(f"❌ Lỗi khi lưu file: {e}")

if __name__ == '__main__':
    get_debug_data()