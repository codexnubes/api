#!flask/bin/python
from flask import Flask, jsonify, request, make_response
from flask_pymongo import PyMongo

app = Flask(__name__)

#Database Config
app.config['MONGO_DBNAME'] = 'ec2-api'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/ec2-api'

mongo = PyMongo(app)

@app.route('/ec2-api/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    framework = mongo.db.api
    output = []
    for q in framework.find():
        output.append({'id': q['_id'], 'app_id': q['app'], 'appGroup': q['appGroup']})
    return jsonify({'result': output})

@app.route('/ec2-api/api/v1.0/tasks/<id>', methods=['GET'])
def get_one_task(id):
    framework = mongo.db.api
    q = framework.find_one({'_id' : id})
    if q:
        output = {'id': q['_id'], 'app_id': q['app'], 'appGroup': q['appGroup']}
    else:
        output = 'No results found'
    return jsonify({'result' : output})

@app.route('/ec2-api/api/v1.0/tasks', methods=['POST'])
def add_tasks():
    framework = mongo.db.api
    id = request.json['id']
    appGroup = request.json['appGroup']
    framework_id = framework.insert({'_id' : id, 'appGroup' : appGroup})
    new_framework = framework.find_one({'_id' : framework_id})
    output = {'id' : new_framework['_id'], 'appGroup' : new_framework['appGroup']}

    return jsonify({'result' : output})

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not Found'}), 404)

@app.errorhandler(500)
def server_error(error):
    return make_response(jsonify({'error': 'Internal Server Error'}), 500)

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad Request'}), 400)

app.run(host= '0.0.0.0')

if __name__ == '__main__':
    app.run(debug=True)

