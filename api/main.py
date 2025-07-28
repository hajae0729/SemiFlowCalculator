from flask import Flask, request, jsonify, send_file, send_from_directory
import io
import os
import base64
from datetime import datetime
import math
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

app = Flask(__name__, static_folder='../frontend', static_url_path='')

# 메모리 히스토리 DB
history = []

@app.route('/api/calculate', methods=['POST'])
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

@app.route('/api/save_history', methods=['POST'])
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

@app.route('/api/save_area_history', methods=['POST'])
def save_area_history():
    data = request.json or {}
    hist = {
        'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'area_camera_res': data.get('area_camera_res'),
        'area_camera_freq': data.get('area_camera_freq'),
        'area_scan_speed': data.get('area_scan_speed'),
        'area_accel_g': data.get('area_accel_g'),
        'area_accel_margin': data.get('area_accel_margin'),
        'area_wafer_size': data.get('area_wafer_size'),
        'area_fov_x': data.get('area_fov_x'),
        'area_fov_y': data.get('area_fov_y'),
        'area_scan_delay': data.get('area_scan_delay'),
        'area_process_delay': data.get('area_process_delay'),
        'area_wafer_change_delay': data.get('area_wafer_change_delay'),
        'scan_time': data.get('area_full_scan_time'),
        'uph': data.get('area_full_scan_uph')
    }
    history.insert(0, hist)
    return jsonify({'status': 'ok'})

@app.route('/api/download_pdf', methods=['POST'])
def download_pdf():
    data = request.json or {}
    screenshot_data = data.get('screenshot', '')
    image_ratio = data.get('imageRatio', 1.0)  # 기본값 1.0 (정사각형)
    
    # 데이터 파싱
    wafer_size = float(data.get('wafer_size', 310))
    scan_speed = float(data.get('scan_speed', 100))
    accel_g = float(data.get('accel_g', 0.3))
    accel_offset = float(data.get('accel_margin', 0))
    fov = float(data.get('fov_pixel', 6000))
    camera_res = float(data.get('camera_res', 0.1875))
    camera_freq = float(data.get('camera_freq', 1000))
    safety_factor = float(data.get('safety_factor', 90))
    scan_delay = float(data.get('scan_delay', 0.35))
    wafer_align_scan_count = int(data.get('wafer_align_scan_count', 1))
    process_delay = float(data.get('process_delay', 5))
    wafer_change_delay = float(data.get('wafer_change_delay', 13))

    # 계산 로직
    UNIT = 1000
    GRAVITY = 9.80665

    def get_accel_time(acceleration, scan_speed):
        if acceleration == 0:
            return 0
        return (scan_speed / UNIT) / (acceleration * GRAVITY)

    def get_accel_distance(acceleration, scan_speed):
        if acceleration == 0:
            return 0
        accel_time = get_accel_time(acceleration, scan_speed)
        return 0.5 * acceleration * GRAVITY * (accel_time ** 2) * 1000

    def get_constant_distance(wafer_size):
        return wafer_size

    def get_total_scan_distance(accel_dist, wafer_size, accel_offset):
        return (2 * accel_dist) + wafer_size + (2 * accel_offset)

    accel_time = get_accel_time(accel_g, scan_speed)
    accel_dist = get_accel_distance(accel_g, scan_speed)
    const_dist = get_constant_distance(wafer_size)
    total_scan_dist = get_total_scan_distance(accel_dist, wafer_size, accel_offset)

    scan_count = math.ceil(wafer_size / (fov * camera_res / 1000)) + wafer_align_scan_count
    full_scan_time = ((total_scan_dist * scan_count) / scan_speed + scan_count * 0.05) + process_delay
    full_scan_uph = 3600 / (full_scan_time + wafer_change_delay) if (full_scan_time + wafer_change_delay) else 0
    circle_scan_time = full_scan_time * 0.95
    circle_scan_uph = 3600 / (circle_scan_time + wafer_change_delay) if (circle_scan_time + wafer_change_delay) else 0

    # PDF 생성 로직
    pdf_output = io.BytesIO()
    c = canvas.Canvas(pdf_output, pagesize=letter)

    # 헤더 및 제목
    c.setFont("Helvetica-Bold", 16)
    c.drawString(1.5 * inch, 10.5 * inch, "Scanning Performance Report")
    
    # 스크린샷이 있으면 먼저 추가
    if screenshot_data and screenshot_data.strip():
        try:
            # base64 이미지 데이터 디코딩
            if ',' in screenshot_data:
                image_data = base64.b64decode(screenshot_data.split(',')[1])
            else:
                image_data = base64.b64decode(screenshot_data)
            
            # 임시 파일로 이미지 저장
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                temp_file.write(image_data)
                temp_file.flush()
                
                # PDF 페이지 최대 너비 계산 (letter 크기 기준)
                # letter 크기: 8.5 x 11 inch
                # 좌우 여백: 1.5 inch씩
                page_width = 8.5 * inch
                left_margin = 1.5 * inch
                right_margin = 1.5 * inch
                max_width = page_width - left_margin - right_margin  # 5.5 inch
                
                # 이미지를 제목 아래에 배치 (PDF 최대 너비에 맞춰 비율 유지)
                img_width = max_width
                img_height = max_width * image_ratio
                c.drawImage(temp_file.name, left_margin, 7 * inch, width=img_width, height=img_height)
                
                # 임시 파일 삭제
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
                    
        except Exception as e:
            print(f"TDI PDF 이미지 처리 중 오류: {e}")
    
    # 통합 테이블 데이터 (입력 파라미터 + 결과값)
    data = [
        ["Category", "Parameter", "Value", "Unit"],
        ["Motion", "Wafer Size", f"{wafer_size}", "mm"],
        ["Motion", "Scan Speed", f"{scan_speed}", "mm/s"],
        ["Motion", "Acceleration", f"{accel_g}", "g"],
        ["Motion", "Accel Margin", f"{accel_offset}", "mm"],
        ["Camera", "FOV", f"{fov}", "pixels"],
        ["Camera", "Resolution", f"{camera_res}", "mm/pixel"],
        ["Camera", "Frequency", f"{camera_freq}", "kHz"],
        ["Camera", "Safety Factor", f"{safety_factor}", "%"],
        ["Process", "Scan Delay", f"{scan_delay}", "s"],
        ["Process", "Wafer Align Scan Count", f"{wafer_align_scan_count}", ""],
        ["Process", "Process Delay", f"{process_delay}", "s"],
        ["", "", "", ""],  # 빈 행으로 구분
        ["Result", "Total Scan Distance", f"{total_scan_dist:.4f}", "mm"],
        ["Result", "Scan Count", f"{scan_count}", ""],
        ["Result", "Full Scan Time", f"{full_scan_time:.4f}", "s"],
        ["Result", "Full Scan UPH", f"{full_scan_uph:.4f}", ""],
        ["Result", "Circle Scan Time", f"{circle_scan_time:.4f}", "s"],
        ["Result", "Circle Scan UPH", f"{circle_scan_uph:.4f}", ""]
    ]

    # PDF 테이블 스타일
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (2, 1), (2, -1), 'RIGHT'),  # 값 열을 오른쪽 정렬
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Category 열을 중앙 정렬
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Parameter 열을 왼쪽 정렬
        ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Unit 열을 중앙 정렬
    ])

    # PDF 테이블 생성
    table = Table(data, colWidths=[0.8 * inch, 2.2 * inch, 1.5 * inch, 0.8 * inch])
    table.setStyle(table_style)

    # PDF 페이지에 테이블 추가 (이미지 아래에 배치)
    table.wrapOn(c, 1.5 * inch, 10 * inch)
    table.drawOn(c, 1.5 * inch, 0.5 * inch)
    
    c.save()
    pdf_output.seek(0)

    return send_file(pdf_output, as_attachment=True, download_name="tdi_scan_performance.pdf", mimetype='application/pdf')

@app.route('/api/download_area_pdf', methods=['POST'])
def download_area_pdf():
    data = request.json or {}
    screenshot_data = data.get('screenshot', '')
    image_ratio = data.get('imageRatio', 1.0)  # 기본값 1.0 (정사각형)
    
    # AREA 데이터 파싱
    area_wafer_size = float(data.get('area_wafer_size', 310))
    area_scan_speed = float(data.get('area_scan_speed', 100))
    area_accel_g = float(data.get('area_accel_g', 0.3))
    area_accel_margin = float(data.get('area_accel_margin', 0))
    area_camera_res = float(data.get('area_camera_res', 1))
    area_camera_freq = float(data.get('area_camera_freq', 100))
    area_safety_factor = float(data.get('area_safety_factor', 90))
    area_fov_x = float(data.get('area_fov_x', 640))
    area_fov_y = float(data.get('area_fov_y', 480))
    area_scan_delay = float(data.get('area_scan_delay', 0.35))
    area_process_delay = float(data.get('area_process_delay', 5))
    area_wafer_change_delay = float(data.get('area_wafer_change_delay', 2))

    # AREA 계산 로직
    UNIT = 1000
    GRAVITY = 9.80665

    def get_accel_time(acceleration, scan_speed):
        if acceleration == 0:
            return 0
        return (scan_speed / UNIT) / (acceleration * GRAVITY)

    def get_accel_distance(acceleration, scan_speed):
        if acceleration == 0:
            return 0
        accel_time = get_accel_time(acceleration, scan_speed)
        return 0.5 * acceleration * GRAVITY * (accel_time ** 2) * 1000

    def get_constant_distance(wafer_size):
        return wafer_size

    def get_total_scan_distance(accel_dist, wafer_size, accel_offset):
        return (2 * accel_dist) + wafer_size + (2 * accel_offset)

    accel_time = get_accel_time(area_accel_g, area_scan_speed)
    accel_dist = get_accel_distance(area_accel_g, area_scan_speed)
    const_dist = get_constant_distance(area_wafer_size)
    total_scan_dist = get_total_scan_distance(accel_dist, area_wafer_size, area_accel_margin)

    # Line Count 계산 (Wafer size * 1000 / (Camera Resolution * Fov X))
    line_count = math.ceil((area_wafer_size * 1000) / (area_camera_res * area_fov_x))
    scan_count = line_count

    line_scan_time = math.ceil(area_wafer_size / (area_camera_res * area_fov_y / 1000)) / (area_camera_freq * (area_safety_factor / 100))
    # Scan Time 계산
    full_scan_time = (accel_time * 2 + area_scan_delay) * scan_count + line_scan_time * scan_count + area_process_delay
    full_scan_uph = 3600 / (full_scan_time + area_wafer_change_delay)
    circle_scan_time = full_scan_time * 0.95
    circle_scan_uph = 3600 / (circle_scan_time + area_wafer_change_delay)

    # PDF 생성 로직
    pdf_output = io.BytesIO()
    c = canvas.Canvas(pdf_output, pagesize=letter)

    # 헤더 및 제목
    c.setFont("Helvetica-Bold", 16)
    c.drawString(1.5 * inch, 10.5 * inch, "Area Scanning Performance Report")
    
    # 스크린샷이 있으면 먼저 추가
    if screenshot_data and screenshot_data.strip():
        try:
            # base64 이미지 데이터 디코딩
            if ',' in screenshot_data:
                image_data = base64.b64decode(screenshot_data.split(',')[1])
            else:
                image_data = base64.b64decode(screenshot_data)
            
            # 임시 파일로 이미지 저장
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                temp_file.write(image_data)
                temp_file.flush()
                
                # PDF 페이지 최대 너비 계산 (letter 크기 기준)
                # letter 크기: 8.5 x 11 inch
                # 좌우 여백: 1.5 inch씩
                page_width = 8.5 * inch
                left_margin = 1.5 * inch
                right_margin = 1.5 * inch
                max_width = page_width - left_margin - right_margin  # 5.5 inch
                
                # 이미지를 제목 아래에 배치 (PDF 최대 너비에 맞춰 비율 유지)
                img_width = max_width
                img_height = max_width * image_ratio
                c.drawImage(temp_file.name, left_margin, 7 * inch, width=img_width, height=img_height)
                
                # 임시 파일 삭제
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
                    
        except Exception as e:
            print(f"AREA PDF 이미지 처리 중 오류: {e}")
    
    # AREA 통합 테이블 데이터
    data = [
        ["Category", "Parameter", "Value", "Unit"],
        ["Motion", "Wafer Size", f"{area_wafer_size}", "mm"],
        ["Motion", "Scan Speed", f"{area_scan_speed}", "mm/s"],
        ["Motion", "Acceleration", f"{area_accel_g}", "g"],
        ["Motion", "Accel Margin", f"{area_accel_margin}", "mm"],
        ["Camera", "FOV X", f"{area_fov_x}", "pixels"],
        ["Camera", "FOV Y", f"{area_fov_y}", "pixels"],
        ["Camera", "Resolution", f"{area_camera_res}", "mm/pixel"],
        ["Camera", "Frame Rate", f"{area_camera_freq}", "fps"],
        ["Camera", "Safety Factor", f"{area_safety_factor}", "%"],
        ["Process", "Scan Delay", f"{area_scan_delay}", "s"],
        ["Process", "Process Delay", f"{area_process_delay}", "s"],
        ["Process", "Wafer Change Delay", f"{area_wafer_change_delay}", "s"],
        ["", "", "", ""],  # 빈 행으로 구분
        ["Result", "Total Scan Distance", f"{total_scan_dist:.4f}", "mm"],
        ["Result", "Line Count", f"{line_count}", ""],
        ["Result", "Scan Count", f"{scan_count}", ""],
        ["Result", "Full Scan Time", f"{full_scan_time:.4f}", "s"],
        ["Result", "Full Scan UPH", f"{full_scan_uph:.4f}", ""],
        ["Result", "Circle Scan Time", f"{circle_scan_time:.4f}", "s"],
        ["Result", "Circle Scan UPH", f"{circle_scan_uph:.4f}", ""]
    ]

    # PDF 테이블 스타일
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (2, 1), (2, -1), 'RIGHT'),  # 값 열을 오른쪽 정렬
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Category 열을 중앙 정렬
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Parameter 열을 왼쪽 정렬
        ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Unit 열을 중앙 정렬
    ])

    # PDF 테이블 생성
    table = Table(data, colWidths=[0.8 * inch, 2.2 * inch, 1.5 * inch, 0.8 * inch])
    table.setStyle(table_style)

    # PDF 페이지에 테이블 추가 (이미지 아래에 배치)
    table.wrapOn(c, 1.5 * inch, 10 * inch)
    table.drawOn(c, 1.5 * inch, 0.5 * inch)
    
    c.save()
    pdf_output.seek(0)

    return send_file(pdf_output, as_attachment=True, download_name="area_scan_performance.pdf", mimetype='application/pdf')

@app.route('/api/history', methods=['GET'])
def get_history():
    return jsonify(history)

@app.route('/api/clear_history', methods=['POST'])
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
