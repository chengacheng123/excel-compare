from flask import Flask, render_template_string
import requests
from datetime import datetime

app = Flask(__name__)

# ===== 配置 =====
API_KEY = "66ebb3ebddcbf79bfa683ad57c8f4c16"
CITY = "xiaogan"
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"

# ===== 天气图标映射（简单用 Unicode 表情）=====
ICONS = {
    "晴": "☀️",
    "云": "☁️",
    "阴": "⛅",
    "雨": "🌧️",
    "雪": "❄️",
    "雷": "⛈️",
    "雾": "🌫️",
    "风": "🌬️"
}


def get_weather_icon(description):
    for key, icon in ICONS.items():
        if key in description:
            return icon
    return "🌤️"


@app.route('/')
def weather_page():
    try:
        # 获取天气数据
        url = f"{WEATHER_URL}?q={CITY}&appid={API_KEY}&units=metric&lang=zh_cn"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            weather_desc = data['weather'][0]['description']
            wind_speed = data['wind']['speed']
            city_name = data['name']
            update_time = datetime.now().strftime("%Y年%m月%d日 %H:%M")
            icon = get_weather_icon(weather_desc)
        else:
            temp = "N/A"
            feels_like = "N/A"
            humidity = "N/A"
            weather_desc = "获取失败"
            wind_speed = "N/A"
            city_name = CITY
            update_time = datetime.now().strftime("%Y年%m月%d日 %H:%M")
            icon = "⚠️"
    except Exception as e:
        temp = "N/A"
        feels_like = "N/A"
        humidity = "N/A"
        weather_desc = "网络错误"
        wind_speed = "N/A"
        city_name = CITY
        update_time = "未知"
        icon = "❌"

    # 内嵌 HTML 页面（单文件，方便部署）
    html = """
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>🌤 {{city_name}} 天气</title>
    <style>
        body {
            font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #74b9ff, #00b4d8);
            color: white;
            text-align: center;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 500px;
            margin: 40px auto;
            padding: 30px 20px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
            backdrop-filter: blur(10px);
        }
        h1 {
            margin: 0 0 10px 0;
            font-size: 28px;
        }
        .icon {
            font-size: 60px;
            margin: 10px 0;
        }
        .temp {
            font-size: 48px;
            font-weight: bold;
            margin: 10px 0;
        }
        .feels {
            font-size: 18px;
            opacity: 0.9;
        }
        .info {
            margin: 20px 0;
            line-height: 2;
            font-size: 16px;
        }
        .update {
            font-size: 14px;
            opacity: 0.8;
            margin-top: 30px;
        }
        .refresh {
            margin-top: 20px;
        }
        button {
            padding: 10px 20px;
            font-size: 16px;
            background: white;
            color: #00b4d8;
            border: none;
            border-radius: 8px;
            cursor: pointer;
        }
        button:hover {
            background: #e0f7fa;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{city_name}}</h1>
        <div class="icon">{{icon}}</div>
        <div class="temp">{{temp}}°C</div>
        <div class="feels">体感 {{feels_like}}°C</div>
        <div class="info">
            <p>🌤 天气：{{weather_desc}}</p>
            <p>💧 湿度：{{humidity}}%</p>
            <p>🌬 风速：{{wind_speed}} m/s</p>
        </div>
        <button onclick="location.reload()">🔄 刷新天气</button>
        <p class="update">更新时间：{{update_time}}</p>
    </div>
</body>
</html>
    """.replace("{{city_name}}", city_name) \
        .replace("{{temp}}", f"{temp:.1f}" if isinstance(temp, float) else str(temp)) \
        .replace("{{feels_like}}", f"{feels_like:.1f}" if isinstance(feels_like, float) else str(feels_like)) \
        .replace("{{weather_desc}}", weather_desc) \
        .replace("{{humidity}}", str(humidity)) \
        .replace("{{wind_speed}}", str(wind_speed)) \
        .replace("{{update_time}}", update_time) \
        .replace("{{icon}}", icon)

    return render_template_string(html)


# ===== 运行服务 =====
if __name__ == '__main__':
    print("🌍 天气网页已启动！访问：http://localhost:5000")
    app.run(host='0.0.0.0', port=5000)