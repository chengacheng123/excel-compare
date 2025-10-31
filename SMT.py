from PIL import Image, ImageDraw, ImageFont
import numpy as np

# -------------------------------
# 1. 配置参数
# -------------------------------
image_path = '湿敏度.png'  # 替换为你的截图路径
output_path = 'jt.png'

# 字体路径（系统自带字体，根据系统选择）
# Windows
# font_path = "C:/Windows/Fonts/simhei.ttf"  # 黑体，支持中文
# macOS
# font_path = "/System/Library/Fonts/STHeiti Light.ttc"
# Linux (如 Ubuntu 安装了中文字体)
font_path = "NotoSansCJK-Regular.ttc"  # 或者下载 simhei.ttf 放在当前目录

# 如果没有中文字体，可以先用默认字体（可能不显示中文）
try:
    font = ImageFont.truetype(font_path, 14)
except:
    font = ImageFont.load_default()  # 注意：默认字体不支持中文！

# 表格起始位置（你需要根据截图手动估算）
# 方法：用看图软件打开截图，鼠标悬停，查看表格第一行第一列的坐标 (x, y)
table_x = 50   # 调整：表格左上角X（大概值）
table_y = 200  # 调整：表格左上角Y（大概值）
row_height = 30
col_widths = [80, 80, 80, 80, 80, 80, 80, 80, 80, 80, 100, 80]  # 每列宽度

# 要插入的数据（示例）
data = [
    ["MS1001", "IC-MSD-001", "2024-03-15", "100", "20", "80", "0.5小时", "-", "未暴露", "正常", "2024-04-01 09:30", "张三"],
    ["MS1002", "IC-MSD-002", "2024-04-01", "50", "15", "35", "2.0小时", "2024-04-02 16:00", "超时暴露", "已报废", "2024-04-02 16:05", "李四"],
    ["MS1003", "IC-MSD-003", "2024-03-28", "200", "0", "200", "0.0小时", "-", "存储中", "正常", "2024-04-03 10:15", "王五"],
    ["MS1004", "IC-MSD-004", "2024-02-20", "80", "30", "50", "1.5小时", "-", "拆分中", "正常", "2024-04-04 14:20", "赵六"]
]

text_color = (0, 0, 0)  # 黑色文字

# -------------------------------
# 2. 加载图片并绘制文字
# -------------------------------
try:
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    y_start = table_y + row_height  # 第一行数据开始的Y坐标（跳过表头）

    for row_idx, row in enumerate(data):
        y = y_start + row_idx * row_height
        x = table_x
        for col_idx, cell_text in enumerate(row):
            # 居中对齐文本
            try:
                bbox = draw.textbbox((0,0), cell_text, font=font)
                text_width = bbox[2] - bbox[0]
            except:
                text_width = len(cell_text) * 10  # 粗略估算
            cell_center_x = x + col_widths[col_idx] // 2
            text_x = cell_center_x - text_width // 2
            draw.text((text_x, y + 5), cell_text, fill=text_color, font=font)
            x += col_widths[col_idx]

    # 保存新图片
    img.save(output_path, "PNG")
    print(f"✅ 成功生成带数据的图片：{output_path}")
    img.show()  # 自动打开图片（可选）

except Exception as e:
    print(f"❌ 错误：{e}")
    print("请检查图片路径、字体路径或坐标是否正确。")