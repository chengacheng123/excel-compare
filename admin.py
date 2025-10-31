# 返回所有用户的列表

from flask import Flask, jsonify, request

# 创建一个 Web 应用
app = Flask(__name__)


users = [
    {"id": 1, "name": "Alice", "email": "alice@example.com","dept" :"MES"},
    {"id": 2, "name": "Bob", "email": "bob@example.com","dept" :"MES"}
]

# === API 接口开始 ===

# GET: 获取所有用户
@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify(users)

# POST: CreateUser
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    new_name = data['name'].strip()
    new_email = data['email'].strip()
    new_dept = data['dept'].strip()
    if not new_dept  :
        return jsonify({"error": "新增失败", "message": "部门不能为空,并且不能是数字"})
    if any(char.isdigit() for char in new_dept) :
        return jsonify({"error": "新增失败", "message": "部门不能为数字"})
    # Name.email 不允许重复,lower()转换为小写作对比
    for user in users:
        if user['name'].lower() == new_name.lower() and user['email'].lower() == new_email.lower():
            return jsonify({"新增失败": f"用户名称 '{new_name}' 已存在"}), 400
    #  新用户的 ID 是最后一个用户的 ID + 1，users[-1] 列表最后一个元素
    new_id = users[-1]['id'] + 1 if users else 1
    new_user = {
        "id": new_id,
        "name": new_name,
        "email": new_email,
        "dept": new_dept
    }
    users.append(new_user)
    return jsonify({"status:":"success","msg":"成功新增","date":new_user}), 201

# GET: 根据 ID 获取单个User
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = None
    for u in users:
        if u['id'] == user_id:
            user = u
            break
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)

# PUT: 更新用户信息
@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = None
    for u in users:
        if u['id'] == user_id:
            user = u
            break
    if user is None:
        return jsonify({"error": "User not found"}), 404
    data = request.get_json()
    user['name'] = data.get('name', user['name'])      # 如果传了就改，没传就保持原样
    user['email'] = data.get('email', user['email'])
    # 获取新的dept值
    new_dept = data.get('dept')
    if new_dept is not None :
        if isinstance(new_dept, str) and new_dept.isdigit():
            return jsonify({
                "error": "更新失败",
                "message": "部门不能为数字"
            }), 400
        user['dept'] = new_dept
    return jsonify(user)


# DELETE: 删除用户
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    global users  # 告诉 Python 我要修改外面的 users 列表
    user = None
    for u in users:
        if u['id'] == user_id:
            user = u
            break
    if user is None:
        return jsonify({"error": "User not found"}), 404

    users = [u for u in users if u['id'] != user_id]  # 删除指定用户
    return jsonify({"message": "User deleted"})

# === 运行服务器 ===
if __name__ == '__main__':
    app.run(debug=True)  # 启动服务器，debug=True 表示出错会提示