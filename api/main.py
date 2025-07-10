from flask import Flask, request, jsonify, send_file, send_from_directory
import pandas as pd
import io
import os
from datetime import datetime
import math

app = Flask(__name__, static_folder='../frontend', static_url_path='')

# 메모리 히스토리 DB
history = []

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json or {}
    # 입력값 파싱
    wafer_size = float(data.get('wafer_size', 310))
    scan_speed = float(data.get('scan_speed', 100))
    accel_g = float(data.get('accel_g', 0.3))
    accel_offset = float(data.get('accel_margin', 0))
    fov = float(data.get('fov_pixel', 6000))
    camera_res = float(data.get('camera_res', 0.1875))
    wafer_align_scan_count = int(data.get('wafer_align_scan_count', 1))
    process_delay = float(data.get('process_delay', 5))
    wafer_change_delay = float(data.get('wafer_change_delay', 13))
    # C# 코드와 동일한 상수
    UNIT = 1000
    GRAVITY = 9.80665

    # 가속 시간 (scanSpeed 단위 변환 필요)
    def get_accel_time(acceleration, scan_speed):
        if acceleration == 0:
            return 0
        return (scan_speed / UNIT) / (acceleration * GRAVITY)

    # 가속 거리
    def get_accel_distance(acceleration, scan_speed):
        if acceleration == 0:
            return 0
        accel_time = get_accel_time(acceleration, scan_speed)
        return 0.5 * acceleration * GRAVITY * (accel_time ** 2) * 1000

    # 등속 거리
    def get_constant_distance(wafer_size):
        return wafer_size

    # 총 스캔 거리
    def get_total_scan_distance(accel_dist, wafer_size, accel_offset):
        return (2 * accel_dist) + wafer_size + (2 * accel_offset)

    # 실제 계산 적용
    accel_time = get_accel_time(accel_g, scan_speed)
    accel_dist = get_accel_distance(accel_g, scan_speed)
    const_dist = get_constant_distance(wafer_size)
    total_scan_dist = get_total_scan_distance(accel_dist, wafer_size, accel_offset)

    # ScanCount 계산 (C#과 동일)
    scan_count = math.ceil(wafer_size / (fov * camera_res / 1000)) + wafer_align_scan_count
    # FullScanTime 계산 (C#과 동일)
    full_scan_time = ((total_scan_dist * scan_count) / scan_speed + scan_count * 0.05) + process_delay
    # FullScanUPH 계산 (C#과 동일)
    full_scan_uph = 3600 / (full_scan_time + wafer_change_delay) if (full_scan_time + wafer_change_delay) else 0
    # CircleScanTime, CircleScanUPH 계산 (C#과 동일)
    circle_scan_time = full_scan_time * 0.95
    circle_scan_uph = 3600 / (circle_scan_time + wafer_change_delay) if (circle_scan_time + wafer_change_delay) else 0

    # 히스토리 저장 코드 제거!
    return jsonify({
        'accel_time': round(accel_time, 4),
        'accel_dist': round(accel_dist, 4),
        'const_dist': round(const_dist, 4),
        'total_scan_dist': round(total_scan_dist, 4),
        'scan_count': scan_count,
        'full_scan_time': round(full_scan_time, 4),
        'full_scan_uph': round(full_scan_uph, 4),
        'circle_scan_time': round(circle_scan_time, 4),
        'circle_scan_uph': round(circle_scan_uph, 4)
    })

@app.route('/save_history', methods=['POST'])
def save_history():
    data = request.json or {}
    hist = {
        'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'camera_res': data.get('camera_res'),
        'camera_freq': data.get('camera_freq'),
        'scan_speed': data.get('scan_speed'),
        'accel_g': data.get('accel_g'),
        'accel_margin': data.get('accel_margin'),
        'wafer_size': data.get('wafer_size'),
        'safety_factor': data.get('safety_factor'),
        'scan_delay': data.get('scan_delay'),
        'process_delay': data.get('process_delay'),
        'wafer_align_scan_count': data.get('wafer_align_scan_count'),
        'fov_pixel': data.get('fov_pixel'),
        'scan_time': data.get('full_scan_time'),
        'uph': data.get('full_scan_uph')
    }
    history.insert(0, hist)
    return jsonify({'status': 'ok'})

@app.route('/download_excel', methods=['POST'])
def download_excel():
    data = request.json or {}
    df = pd.DataFrame([data])
    output = io.BytesIO()
    # type: ignore
    df.to_excel(output, index=False, engine='xlsxwriter')
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="result.xlsx", mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/history', methods=['GET'])
def get_history():
    return jsonify(history)

@app.route('/clear_history', methods=['POST'])
def clear_history():
    global history
    history.clear()
    return jsonify({'status': 'ok'})

# 정적 파일 서빙
@app.route('/')
def root():
    if app.static_folder:
        return send_from_directory(app.static_folder, 'index.html')
    return "Static folder not configured", 404

@app.route('/<path:path>')
def static_proxy(path):
    if app.static_folder:
        return send_from_directory(app.static_folder, path)
    return "Static folder not configured", 404

if __name__ == "__main__":
    app.run(debug=False, use_reloader=False) 
