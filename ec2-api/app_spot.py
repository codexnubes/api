#!flask/bin/python
from flask import Flask, jsonify, request, make_response
from flask_pymongo import PyMongo

app = Flask(__name__)

#Database Config
app.config['MONGO_DBNAME'] = 'spot'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/spot'

mongo = PyMongo(app)

@app.route('/spot/api/v1.0/get_data/all', methods=['GET'])
def get_data():
   framework = mongo.db.data
   output = []
   os_array=[]

   for z in framework.find():
        for x in z['regions'][0]['instanceTypes']:
            os_array.append({'region':z['regions'][0]['region'], 'date': z['date'], 'time': z['time'], 'currency': z['currency'], 'os':x["os"], 'type':x['type'], 'price': x['price'], 'utilization': x['utilization']})

   return jsonify({'result': os_array})

@app.route('/spot/api/v1.0/get_region/<region>', methods=['GET'])
def get_one_region(region):
    framework = mongo.db.data
    os_array=[]
    
    t= framework.find_one({'regions.region':region})
    
    for z in t:
        print z
        if z == "regions":
            for x in t[z][0]['instanceTypes']:
                print x
                os_array.append({'region':region, 'date': t['date'], 'time': t['time'], 'currency': t['currency'], 'os':x["os"], 'type':x['type'], 'price': x['price'], 'utilization': x['utilization']})

    return jsonify({'result': os_array})

@app.route('/spot/api/v1.0/get_family/<family>', methods=['GET'])
def get_one_family(family):
    framework = mongo.db.data
    os_array=[]

    t= framework.find_one({'regions.instanceTypes.type':family})
    print t

    return jsonify({'result': os_array})


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
    app.run(debug=True, port=5000)

