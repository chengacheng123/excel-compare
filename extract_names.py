# -*- coding: utf-8 -*-
"""
从远程共享文件夹读取 .txt 日志，提取 name 字段，并保存到本地 CSV
"""
import os
import re
import csv
from datetime import datetime

# ==================== 配置区（你只需要改这里）====================
REMOTE_LOG_DIR = r'\\192.168.1.100\logs'  # 对方电脑的共享文件夹路径
LOCAL_SAVE_DIR = './extracted_logs'  # 本地保存结果的文件夹


# ================================================================

def main():
    # 1. 创建本地保存目录
    os.makedirs(LOCAL_SAVE_DIR, exist_ok=True)

    # 2. 检查远程文件夹是否存在
    if not os.path.exists(REMOTE_LOG_DIR):
        print("❌ 错误：无法访问远程路径，请检查：")
        print("   - 对方是否开启了文件夹共享")
        print("   - 网络是否通畅")
        print("   - 路径是否正确")
        return

    # 3. 找到所有 .txt 日志文件
    txt_files = [f for f in os.listdir(REMOTE_LOG_DIR) if f.endswith('.txt')]
    if not txt_files:
        print("🟡 未找到任何 .txt 日志文件")
        return

    print(f"📁 发现 {len(txt_files)} 个日志文件：{txt_files}")

    # 4. 存放提取到的 name
    names = []

    # 5. 遍历每个文件
    for filename in txt_files:
        file_path = os.path.join(REMOTE_LOG_DIR, filename)
        print(f"\n📄 正在读取: {filename}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    # 使用正则提取 name=xxx
                    match = re.search(r'name=([^|\s]+)', line)
                    if match:
                        name = match.group(1)
                        names.append(name)
                        print(f"   ✅ 第 {line_num} 行 -> {name}")
        except Exception as e:
            print(f"❌ 读取 {filename} 失败: {e}")

    # 6. 如果没提取到数据
    if not names:
        print("🟡 未在日志中找到任何 name 字段")
        return

    # 7. 生成带时间戳的文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"{LOCAL_SAVE_DIR}/names_{timestamp}.csv"

    # 8. 保存到 CSV
    with open(csv_filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Extract Time'])
        extract_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for name in names:
            writer.writerow([name, extract_time])

    # 9. 完成提示
    print(f"\n🎉 提取完成！")
    print(f"📊 共找到 {len(names)} 个 name：{names}")
    print(f"💾 已保存到：{csv_filename}")


# ============ 运行 ============
if __name__ == '__main__':
    main()