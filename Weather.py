import requests
from datetime import datetime

# ===== 1. 天气配置 =====
API_KEY = "66ebb3ebddcbf79bfa683ad57c8f4c16"  # OpenWeatherMap 密钥
CITY = "Xiaogan"  # 城市英文名
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"

# ===== 2. Server酱配置（你自己的密钥）=====
SEND_KEY = "SCT300200TVAR52tbIvKYQOTg3x5AL5eV0"  # 你的 SendKey
PUSH_URL = f"https://sctapi.ftqq.com/{SEND_KEY}.send"


def get_weather():
    try:
        # 获取天气数据
        url = f"{WEATHER_URL}?q={CITY}&appid={API_KEY}&units=metric&lang=zh_cn"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()

            # 提取信息
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            weather = data['weather'][0]['description']
            wind_speed = data['wind']['speed']
            city_name = data['name']
            update_time = datetime.now().strftime("%H:%M:%S")

            # 📱 微信推送标题
            title = f"🌤 {city_name} 实时天气 | {temp:.1f}°C"

            # 📱 微信推送内容（支持 Markdown 风格）
            content = f"""
# 🌤 {city_name} 天气播报

⏰ 更新时间：{update_time}

---

🌡 **温度**：{temp:.1f}°C  
（体感 {feels_like:.1f}°C）

💧 **湿度**：{humidity}%

🌬 **风速**：{wind_speed} m/s

🌦 **天气**：{weather}

---

✅ 数据来自 OpenWeatherMap  
（每运行一次发送一条）
            """.strip()

            # 发送 POST 请求到 Server酱
            push_data = {
                "title": title,
                "desp": content
            }
            res = requests.post(PUSH_URL, data=push_data)

            if res.status_code == 200:
                print(f"[{update_time}] ✅ 天气消息已成功发送到微信！")
            else:
                print(f"❌ 推送失败，状态码：{res.status_code}")

        else:
            print(f"❌ 天气请求失败，状态码：{response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ 程序错误：{e}")


# ===== 运行函数 =====
if __name__ == "__main__":
    print("🌤 正在获取天气并发送到微信...")
    get_weather()