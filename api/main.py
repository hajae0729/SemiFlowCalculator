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
    data = request.json
    wafer_size = float(data.get('wafer_size', 310))
    scan_speed = float(data.get('scan_speed', 100))
    accel_g = float(data.get('accel_g', 0.3))
    accel_time = float(data.get('accel_time', 0))
    accel_dist = float(data.get('accel_dist', 0))
    scan_const_dist = float(data.get('scan_const_dist', 0))
    scan_total_dist = float(data.get('scan_total_dist', 0))
    # 구간별 시간 계산(예시)
    accel_section = accel_dist if accel_dist > 0 else wafer_size * 0.1
    decel_section = accel_section
    const_section = wafer_size - accel_section - decel_section
    accel_time_sec = accel_section / (scan_speed/2) if scan_speed else 0
    const_time_sec = const_section / scan_speed if scan_speed else 0
    decel_time_sec = decel_section / (scan_speed/2) if scan_speed else 0
    full_scan_time = round(accel_time_sec + const_time_sec + decel_time_sec, 2)
    uph = round(3600 / full_scan_time, 2) if full_scan_time else 0
    # 원형 스캔: 내접 원 면적 비율만큼 시간 단축
    # wafer_area = pi * r^2, circle_area = pi * (r/sqrt(2))^2 = wafer_area/2
    wafer_area = math.pi * (wafer_size/2)**2
    circle_area = wafer_area / 2
    area_ratio = circle_area / wafer_area  # = 0.5
    circle_scan_time = round(full_scan_time * area_ratio, 2)
    circle_uph = round(3600 / circle_scan_time, 2) if circle_scan_time else 0
    # 히스토리 저장
    hist = {
        'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'wafer_size': wafer_size,
        'scan_speed': scan_speed,
        'scan_time': full_scan_time,
        'uph': uph
    }
    history.insert(0, hist)
    return jsonify({
        'full_scan_time': full_scan_time,
        'full_uph': uph,
        'circle_scan_time': circle_scan_time,
        'circle_uph': circle_uph
    })

@app.route('/download_excel', methods=['POST'])
def download_excel():
    data = request.json
    df = pd.DataFrame([data])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="result.xlsx", mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/history', methods=['GET'])
def get_history():
    return jsonify(history)

# 정적 파일 서빙
@app.route('/')
def root():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

if __name__ == "__main__":
    app.run(debug=True) 