from flask import Flask, render_template
import json
import os
import matplotlib.pyplot as plt
import io
import base64
from collections import Counter
from datetime import datetime, timedelta

app = Flask(__name__)

def load_data():
    file_path = os.path.join(os.path.dirname(__file__), 'data_all.json')
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def count_hourly_occurrences(data):
    hourly_counts = {}
    for item in data:
        if "@timestamp" in item:
            timestamp = item["@timestamp"]
            dt_obj = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
            hour = dt_obj.strftime("%H")
            hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
    return hourly_counts

def add_seven_hours(hourly_counts):
    hours_to_update = list(hourly_counts.keys())
    for hour in hours_to_update:
        dt_obj = datetime.strptime(hour, "%H")
        dt_obj += timedelta(hours=7)
        hour_updated = dt_obj.strftime("%H") + ':00'
        hourly_counts[hour_updated] = hourly_counts.pop(hour)
    return hourly_counts

@app.route('/stacked_bar')
def stacked_bar_chart():
    data = load_data()
    hourly_counts = count_hourly_occurrences(data)
    hourly_counts = add_seven_hours(hourly_counts)
    hours_sorted = sorted(hourly_counts.keys())
    counts = [hourly_counts[hour] for hour in hours_sorted]

    plt.figure(figsize=(12, 6))
    plt.bar(hours_sorted, counts)
    plt.xlabel('Hour')
    plt.ylabel('Count')
    plt.title('Data Count by Hour')
    plt.xticks(rotation=45, ha='right')
    plt.grid(True)

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    graph_b64 = base64.b64encode(img.getvalue()).decode()
    return graph_b64

@app.route('/line_plot')
def line_plot():
    data = load_data()
    hourly_counts = count_hourly_occurrences(data)
    hourly_counts = add_seven_hours(hourly_counts)
    hours_sorted = sorted(hourly_counts.keys())
    counts = [hourly_counts[hour] for hour in hours_sorted]

    plt.figure(figsize=(12, 6))
    plt.plot(hours_sorted, counts, marker='o', linestyle='-')
    plt.xlabel('Hour')
    plt.ylabel('Count')
    plt.title('Hourly Occurrences Over Time')
    plt.xticks(rotation=45, ha='right')
    plt.grid(True)

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    graph_b64 = base64.b64encode(img.getvalue()).decode()
    return graph_b64
    
@app.route('/')
def index():
    stacked_bar_graph = stacked_bar_chart()
    line_plot_graph = line_plot()
    return render_template('home.html', stacked_bar_graph=stacked_bar_graph, line_plot_graph=line_plot_graph)

if __name__ == '__main__':
    app.run(debug=True)
