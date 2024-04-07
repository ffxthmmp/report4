from flask import Flask, render_template,jsonify
import io
import base64
import numpy as np
import matplotlib.pyplot as plt
import json
from datetime import datetime, timedelta
import getdata

app = Flask(__name__)

# คำสั่งในการกำหนด backend ของ Matplotlib เป็น Agg
import matplotlib
matplotlib.use('Agg')

# ฟังก์ชันสำหรับโหลดข้อมูลจากไฟล์ JSON
@app.route('/getdata')
def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

# ฟังก์ชันสำหรับแปลงพล็อตเป็นรูปภาพ base64
def plot_to_base64(plot):
    # แปลงพล็อตเป็นรูปภาพ PNG
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # เข้ารหัสรูปภาพเป็น base64
    image_png = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # ส่งคืน URL ข้อมูลสำหรับรูปภาพ
    return f'data:image/png;base64,{image_png}'

# ฟังก์ชันสำหรับนับจำนวนครั้งที่เกิดในแต่ละชั่วโมง
def count_hourly_occurrences(data):
    # สร้างเก็บจำนวนรายการที่เกิดขึ้นในแต่ละชั่วโมง
    hourly_counts = {}
    
    # วนลูปผ่านทุกข้อมูลในรายการข้อมูล
    for item in data:
        if "@timestamp" in item:
            # ดึงค่า timestamp จากข้อมูล
            timestamp = item["@timestamp"]
            # แปลง timestamp เป็นวัตถุ datetime
            dt_obj = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
            # แปลงวัตถุ datetime เป็นสตริงที่มีรูปแบบ "HH" เพื่อใช้ในการระบุชั่วโมงของวัน
            hour = dt_obj.strftime("%H") 
            # เพิ่มหนึ่งเมื่อพบชั่วโมงที่เหมือนกันอีกครั้ง หรืออัปเดตค่านับใน hourly_counts
            hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
            print(hourly_counts)
    
    return hourly_counts


# ฟังก์ชันสำหรับเพิ่ม 7 ชั่วโมงให้กับเวลา
def add_seven_hours(hourly_counts):
    hours_to_update = list(hourly_counts.keys())  # สร้างรายการคีย์ที่คัดลอกจากพจนานุกรม
    for hour in hours_to_update:
        dt_obj = datetime.strptime(hour, "%H")
        dt_obj += timedelta(hours=7)
        hour_updated = dt_obj.strftime("%H") + ':00'
        hourly_counts[hour_updated] = hourly_counts.pop(hour)
    return hourly_counts

# ฟังก์ชันสร้างกราฟเส้น
def generate_line_chart(hourly_counts):
    hours = list(hourly_counts.keys())
    counts = list(hourly_counts.values())

    print(type(hours))

    fig, ax = plt.subplots()
    ax.plot(hours, counts, marker='o')
    ax.set_xlabel('Hour')
    ax.set_ylabel('Packet')
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()

    # แปลงพล็อตเป็น base64
    line_chart = plot_to_base64(fig)

    plt.close(fig)  # ปิดรูปภาพเพื่อปล่อยทรัพยากร
    return line_chart


# ฟังก์ชันสร้างกราฟแท่ง
def generate_bar_chart(hourly_counts):
    hours = list(hourly_counts.keys())
    counts = list(hourly_counts.values())

    fig, ax = plt.subplots()
    ax.bar(hours, counts)
    ax.set_xlabel('Hour')
    ax.set_ylabel('Packet')
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()

    # แปลงพล็อตเป็น base64
    bar_chart = plot_to_base64(fig)

    plt.close(fig)  # ปิดรูปภาพเพื่อปล่อยทรัพยากร
    return bar_chart

@app.route('/')
def index():
    file_path = 'data_all.json'
    data = load_data(file_path)
    hourly_counts = count_hourly_occurrences(data)
    hourly_counts_plus_seven = add_seven_hours(hourly_counts)
    line_chart = generate_line_chart(hourly_counts_plus_seven)
    bar_chart = generate_bar_chart(hourly_counts_plus_seven)
    return render_template('index.html', line=line_chart, bar=bar_chart)

@app.route('/getchart')
def get_json():
    getdata.getdata()
    file_path = 'data_all.json'
    data = load_data(file_path)
    hourly_counts = count_hourly_occurrences(data)
    hourly_counts_plus_seven = add_seven_hours(hourly_counts)
    line_chart = generate_line_chart(hourly_counts_plus_seven)
    bar_chart = generate_bar_chart(hourly_counts_plus_seven)
    data = {
        'line_chart': line_chart,
        'bar_chart': bar_chart
    }

    return jsonify(data)



if __name__ == '__main__':
    app.run(debug=True)
