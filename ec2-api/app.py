#!flask/bin/python
from flask import Flask
from flask_restful import reqparse
from flask import request
from flask import jsonify
from flask import make_response
from flask_httpauth import HTTPBasicAuth
from pymongo import MongoClient
from bson import json_util
import pprint
import flask
'''
/api/v1.0/get_data/all
/api/v1.0/get_region/<region>
/api/v1.0/get_family/<family>
/api/v1.0/get_os/<os>
/api/v1.0/query?date=2017-02-10&region=us-east-1&type=m3.medium
/api/v1.0/query?date=2017-02-10
/api/v1.0/query?date=2017-02-10&region=us-east-1
'''
auth = HTTPBasicAuth()
'''
client = MongoClient('mongodb://ds153978179.mlab.com:53179/')
db = client['ec2-api']
db.authenticate('test','gvh5678')
collection = db['data']
'''
client = MongoClient('mongodb://ds153179.mlab.com:53179/')
db = client['ec2-api']
db.authenticate('test','123456')
collection = db['data']

app = Flask(__name__)

@auth.get_password
def get_username(username):
    if username == 'admin':
        return 'admin'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

@app.route('/')
def index():
	return flask.render_template('index.html')

@app.route('/api/v1.0/get_data/all', methods=['GET'])
@auth.login_required
def get_data():
   data_array=[]

   for all_data in collection.find():
        for data_in_array in all_data['regions'][0]['instanceTypes']:
            data_array.append({'region':all_data['regions'][0]['region'], 'date': all_data['date'], 'time': all_data['time'], 'currency': all_data['currency'], 'os':data_in_array["os"], 'type':data_in_array['type'], 'price': data_in_array['price'], 'utilization': data_in_array['utilization']})

   return jsonify({'result': data_array})

@app.route('/api/v1.0/get_region/<region>', methods=['GET'])
@auth.login_required
def get_region(region):
    region_array=[]
    
    query = collection.find()
    for all_data in query:
        for region_data_array in all_data:
            if region_data_array == "regions":
                for get_price_data in all_data[region_data_array][0]['instanceTypes']:
                    region_array.append({'region':region, 'date': all_data['date'], 'time': all_data['time'], 'currency': all_data['currency'], 'os':get_price_data["os"], 'type':get_price_data['type'], 'price': get_price_data['price'], 'utilization': get_price_data['utilization']})

    return jsonify({'result': region_array})

@app.route('/api/v1.0/get_family/<family>', methods=['GET'])
@auth.login_required
def get_family(family):
    family_array=[]

    query = collection.find()
    for all_data in query:
        for region_data_array in all_data['regions']:
            for get_price_data in region_data_array:
                if get_price_data == 'instanceTypes':
                    for get_family_data_array in region_data_array[get_price_data]:                    
                        if get_family_data_array['type'] == family:
                            family_array.append(get_family_data_array)
    return jsonify({'result': family_array})

@app.route('/api/v1.0/get_os/<os>', methods=['GET'])
@auth.login_required
def get_os(os):
    os_array=[]

    query = collection.find()
    for all_data in query:
        for region_data_array in all_data['regions']:
            for get_price_data in region_data_array:
                if get_price_data == 'instanceTypes':
                    for get_os_data_array in region_data_array[get_price_data]:                       
                        if get_os_data_array['os'] == os:
                            os_array.append(get_os_data_array)
    return jsonify({'result': os_array})

@app.route('/api/v1.0/query')
@auth.login_required
def run():
	parser = reqparse.RequestParser()
	parser.add_argument('date', help= 'Invalid Date')
	parser.add_argument('region', help = 'Invalid Region')
	parser.add_argument('type',help = 'Invalid Type')
	args = parser.parse_args()

	if args['date'] ==None :
		return jsonify(date=args['date'],region = args['region'],type = args['type'])
	else:
		if args['type']==None and args['region'] == None:
			return json_util.dumps(collection.find({'date':args['date']}))
		elif args['type'] ==None:
			return json_util.dumps(collection.find({'date':args['date'],'regions.region':args['region']}))
		else:
			x = collection.find_one({'date':args['date'],'regions.region':args['region']})
			if x!=None and x['regions']!=None and x['regions'][0]!=None:
				for instance in x['regions'][0]['instanceTypes']:
					if instance['type']==args['type']:
						print(instance['price'])
						return json_util.dumps(instance)
				return json_util.dumps([])
			else:
				return json_util.dumps([])

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
	app.run(debug=True, port=80)

