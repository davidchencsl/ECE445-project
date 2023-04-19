from flask import Flask, request
import json
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    return json.dumps({'l_speed': 0.5,
                        'r_speed': 0.5,
                        'l_pwm': 129,
                        'r_pwm': 129,
                        'distance': 0.5,
                       })

@app.route('/api/controls', methods=['POST'])
def set_controls():
    data = request.json
    print(data)
    return 'OK'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6969)