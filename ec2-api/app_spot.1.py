#!flask/bin/python
from flask import Flask, jsonify, request, make_response
from flask_pymongo import PyMongo

app = Flask(__name__)

#Database Config
app.config['MONGO_DBNAME'] = 'ec2-api'
app.config['MONGO_URI'] = 'mongodb://api:123456@ds153179.mlab.com:53179/ec2-api'

mongo = PyMongo(app)

@app.route('/')
def index():
    output = []
    get_region = "/spot/api/v1.0/get_region/<region>"
    get_all = "/spot/api/v1.0/get_data/all"
    get_family = "spot/api/v1.0/get_family/<family>"
    get_os = "/spot/api/v1.0/get_os/<os>"

    output.append({'get_region': get_region, 'get_all': get_all, 'get_family': get_family, 'get_os': get_os})

    return jsonify({'EC2 Spot Pricing API': output})

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
def get_region(region):
    framework = mongo.db.data
    os_array=[]
    
    t= framework.find()

    for z in t:
        for h in z:
            if h == "regions":
                for x in z[h][0]['instanceTypes']:
                    os_array.append({'region':region, 'date': z['date'], 'time': z['time'], 'currency': z['currency'], 'os':x["os"], 'type':x['type'], 'price': x['price'], 'utilization': x['utilization']})

    return jsonify({'result': os_array})

@app.route('/spot/api/v1.0/get_family/<family>', methods=['GET'])
def get_family(family):
    framework = mongo.db.data
    os_array=[]

    t= framework.find()
    for x in t:
        for z in x['regions']:
            for n in z:
                if n == 'instanceTypes':
                    for j in z[n]:                    
                        if j['type'] == family:
                            os_array.append(j)
    return jsonify({'result': os_array})

@app.route('/spot/api/v1.0/get_os/<os>', methods=['GET'])
def get_os(os):
    framework = mongo.db.data
    os_array=[]

    t= framework.find()
    for x in t:
        for z in x['regions']:
            for n in z:
                if n == 'instanceTypes':
                    for j in z[n]:                       
                        if j['os'] == os:
                            os_array.append(j)
    return jsonify({'result': os_array})

@app.route('/spot/api/v1.0/query', methods=['GET'])
def get_query():
    date = request.args.get('date')
    print (date)
    region = request.args.get('region')
    print (region)
    family = request.args.get('family')
    print (family)

    framework = mongo.db.data
    family_array=[]
    region_array=[]
    final_array=[]

    t= framework.find()
    for x in t:
        for z in x['regions']:
            for n in z:
                if n == 'instanceTypes':
                    for j in z[n]:                    
                        if j['type'] == family:
                            family_array.append({'family': j['type'] })
    
    t= framework.find()
    for a in t:
        for h in a:
            if h == "regions":
                for x in a[h][0]['instanceTypes']:
                    region_array.append({'region':region })

    return jsonify({'result': family_array, 'result2': region_array})

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

