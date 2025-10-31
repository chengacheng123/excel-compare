import random
import string


def generate_password(length, use_lowercase=True, use_uppercase=True, use_digits=True, use_symbols=True):
    """
    生成一个随机密码。
    """

    # 定义字符池
    char_pool = ""
    if use_lowercase:
        char_pool += string.ascii_lowercase  # 'abcdefghijklmnopqrstuvwxyz'
    if use_uppercase:
        char_pool += string.ascii_uppercase  # 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if use_digits:
        char_pool += string.digits  # '0123456789'
    if use_symbols:
        char_pool += "!@#$%^&*()_+-=[]{}|;:,.<>?"

    # 安全检查
    if not char_pool:
        print("❌ 错误：至少需要选择一种字符类型！")
        return None

    # 生成密码
    password = ''.join(random.choice(char_pool) for _ in range(length))
    return password


# === 主程序开始 ===
print("🔐 欢迎使用简易密码生成器！")

try:
    length = int(input("请输入密码长度 (建议8-20): "))
    if length < 4:
        print("⚠️  密码太短了！至少需要4位以保证基本安全。")
        length = 4

    print("\n请选择密码包含的字符类型:")
    use_lower = input("包含小写字母? (y/n, 默认是): ").lower() != 'n'
    use_upper = input("包含大写字母? (y/n, 默认是): ").lower() != 'n'
    use_digit = input("包含数字? (y/n, 默认是): ").lower() != 'n'
    use_symbol = input("包含特殊符号? (y/n, 默认是): ").lower() != 'n'

    password = generate_password(length, use_lower, use_upper, use_digit, use_symbol)

    if password:
        print(f"\n✅ 生成的密码: {password}")
        print("💡 提示：请将密码保存在安全的地方！")

except ValueError:
    print("❌ 错误：请输入有效的数字！")
except Exception as e:
    print(f"❌ 发生了一个错误: {e}")

