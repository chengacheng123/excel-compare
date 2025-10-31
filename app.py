from flask import Flask, jsonify

app = Flask(__name__)

people = [
    {'name': 'kai', 'age': '18'},
    {'name': 'zi', 'age': '19'},
    {'name': 'ge', 'age': '20'}
]

full_name = ""
for person in people:
    full_name += person['name']

@app.route('/api/names')
def get_names():
    return jsonify({
        "full_name": full_name,
        "details": people
    })

# Render 需要这个
if __name__ != '__main__':
    app.debug = False