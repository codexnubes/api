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
import socket
import redis
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

#mongo connection
'''
client = MongoClient('mongodb://ds153179.mlab.com:53179/')
db = client['ec2-api']
db.authenticate('test','123456')
collection = db['data']
'''

client = MongoClient('mongodb://ec2-52-33-101-11.us-west-2.compute.amazonaws.com:27017')
db = client['spot']
collection = db['spotinstance']

#test mongo connection
s = socket.socket()
address = 'ec2-52-33-101-11.us-west-2.compute.amazonaws.com'
port = 27017
try:
    s.connect((address, port))
    print s
    print 'MongoDB Connected!'
except Exception as e:
    print s
    print("Failed to connect MongoDB %s:%d. Exception is %s" % (address, port, e))
finally:
    s.close()

#redis connection
try:
    conn = redis.StrictRedis(
        host='127.0.0.1',
        port=6379,
        password='kiFYmWZB8F'
    )
    print conn
    conn.ping()
    print 'Redis Connected!'
except Exception as ex:
    print 'Error:', ex
    exit('Failed to connect redis, terminating')

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
    if conn.get("cache_all_query") ==None:
        for all_data in collection.find():
            for data_in_array in all_data['regions'][0]['instanceTypes']:
                data_array.append({'region':all_data['regions'][0]['region'], 'date': all_data['date'], 'time': all_data['time'], 'currency': all_data['currency'], 'os':data_in_array["os"], 'type':data_in_array['type'], 'price': data_in_array['price'], 'utilization': data_in_array['utilization']})
        conn.set("cache_all_query", data_array)
        return jsonify({'result': data_array})
    else:
        redis_all_q = conn.get("cache_all_query")
        return redis_all_q

@app.route('/api/v1.0/get_region/<region>', methods=['GET'])
@auth.login_required
def get_region(region):
    region_array=[]
    if conn.get("cache_region_query") ==None:
        query = collection.find()
        for all_data in query:
            for region_data_array in all_data:
                if region_data_array == "regions":
                    for get_price_data in all_data[region_data_array][0]['instanceTypes']:
                        region_array.append({'region':region, 'date': all_data['date'], 'time': all_data['time'], 'currency': all_data['currency'], 'os':get_price_data["os"], 'type':get_price_data['type'], 'price': get_price_data['price'], 'utilization': get_price_data['utilization']})
        conn.set("query_region_query", region_array)
        return jsonify({'result': region_array})
    else:
        redis_region_q = conn.get("cache_region_query")
        return redis_region_q

@app.route('/api/v1.0/get_family/<family>', methods=['GET'])
@auth.login_required
def get_family(family):
    family_array=[]
    if conn.get("cache_family_query") ==None:
        query = collection.find()
        for all_data in query:
            for region_data_array in all_data['regions']:
                for get_price_data in region_data_array:
                    if get_price_data == 'instanceTypes':
                        for get_family_data_array in region_data_array[get_price_data]:                    
                            if get_family_data_array['type'] == family:
                                family_array.append(get_family_data_array)
        conn.set("cache_family_query", family_array)
        return jsonify({'result': family_array})
    else:
        redis_family_q = conn.get("cache_family_query")
        return redis_family_q

@app.route('/api/v1.0/get_os/<os>', methods=['GET'])
@auth.login_required
def get_os(os):
    os_array=[]
    if conn.get("cache_os_query") ==None:
        query = collection.find()
        for all_data in query:
            for region_data_array in all_data['regions']:
                for get_price_data in region_data_array:
                    if get_price_data == 'instanceTypes':
                        for get_os_data_array in region_data_array[get_price_data]:                       
                            if get_os_data_array['os'] == os:
                                os_array.append(get_os_data_array)
        conn.set("cache_os_query", os_array)
        return jsonify({'result': os_array})
    else:
        redis_os_q = conn.get("cache_os_query")
        return redis_os_q

@app.route('/api/v1.0/query')
@auth.login_required
def run():
    parser = reqparse.RequestParser()
    parser.add_argument('date', help= 'Invalid Date')
    parser.add_argument('time', help= 'Invalid Time')
    parser.add_argument('os', help= 'Invalid OS Type')
    parser.add_argument('region', help = 'Invalid Region')
    parser.add_argument('type',help = 'Invalid Type')
    args = parser.parse_args()

    if args['date'] ==None :
        return jsonify(date=args['date'],time=args['time'],os=args['os'],region = args['region'],type = args['type'])
    else:
        if args['time']==None and args['os']==None and args['type']==None and args['region'] == None:
            if conn.get("query_date") == None:
                date_query = collection.find({'date':args['date']})
                date_query_json = json_util.dumps(date_query)
                conn.set("query_date", date_query_json)
                return date_query_json
            else:
                redis_date_q = conn.get("query_date")
                return redis_date_q
        if args['os']==None and args['type']==None and args['region']==None:
            if conn.get("query_time") == None:
                time_query = collection.find({'date':args['date'],'time':args['time']})
                time_query_json = json_util.dumps(time_query)
                conn.set("query_time", time_query_json)
                return time_query_json
            else:
                redis_time_q = conn.get("query_time")
                return redis_time_q
        if args['type']==None and args['region']==None:
            if conn.get("query_os") == None:
                os_query = collection.find({'date':args['date'],'time':args['time'],'regions.instanceTypes.os':args['os']})
                os_query_json = json_util.dumps(os_query)
                conn.set("query_os", os_query_json)
                return os_query_json
            else:
                redis_os_q = conn.get("query_os")
                return redis_os_q
        elif args['type'] ==None:
            if conn.get("query_region") == None:
                region_query = collection.find({'date':args['date'],'time':args['time'],'regions.instanceTypes.os':args['os'],'regions.region':args['region']})
                region_query_json = json_util.dumps(region_query)
                conn.set("query_region", region_query_json)
                return region_query_json
            else:
                redis_region_q = conn.get("query_region")
                return redis_region_q
        else:
            if conn.get("query_type") == None: 
                x = collection.find_one({'date':args['date'],'time':args['time'],'regions.instanceTypes.os':args['os'],'regions.region':args['region']})
                if x!=None and x['regions']!=None and x['regions'][0]!=None:
                    for instance in x['regions'][0]['instanceTypes']:
                        if instance['type']==args['type']:
                            print(instance['price'])
                            type_query_json = json_util.dumps(instance)
                            conn.set("query_type", type_query_json)
                            return type_query_json
                    return jsonify({'results': 'Input Error, Try again'})
                else:
                    return jsonify({'results': 'Something went wrong, Try again'})
            else:
                redis_type_q = conn.get("query_type")
                return redis_type_q

@app.route('/api/v1.0/query_range')
@auth.login_required
def query_range():
    parser = reqparse.RequestParser()
    parser.add_argument('min_date', help= 'Invalid Minimum Date')
    parser.add_argument('max_date', help= 'Invalid Maximum Date')
    parser.add_argument('min_time', help= 'Invalid Minimum Time')
    parser.add_argument('max_time', help= 'Invalid Maximum Time')
    parser.add_argument('region', help= 'Invalid Region')
    parser.add_argument('type', help= 'Invalid Type')
    args = parser.parse_args()

    if args['min_date']==None or args['max_date']==None:
        return jsonify(min_date=args['min_date'],max_date=args['max_date'],min_time=args['min_time'],max_time=args['max_time'])
    else:
        if args['min_time']==None and args['max_time']==None:
            date_range_q = collection.find({'date': {'$gte': args['min_date'], '$lte': args['max_date']}})
            return json_util.dumps(date_range_q)
        if args['region']==None and args['type']==None:
            date_time_range_q = collection.find({'date': {'$gte': args['min_date'], '$lte': args['max_date']}, 'time': {'$gte': args['min_time'], '$lte': args['max_time']}})
            return json_util.dumps(date_time_range_q)
        if args['type']==None:
            date_time_region_range_q = collection.find({'date': {'$gte': args['min_date'], '$lte': args['max_date']}, 'time': {'$gte': args['min_time'], '$lte': args['max_time']}, 'regions.region': args['region']})
            return json_util.dumps(date_time_region_range_q)
        else:
            type_array=[]
            date_time_region_type_range_q = collection.find({'date': {'$gte': args['min_date'], '$lte': args['max_date']}, 'time': {'$gte': args['min_time'], '$lte': args['max_time']}, 'regions.region': args['region']})
            for all_data in date_time_region_type_range_q:
                for region_data_array in all_data['regions']:
                    for get_price_data in region_data_array:
                        if get_price_data == 'instanceTypes':
                            for get_type_data_array in region_data_array[get_price_data]:                    
                                if get_type_data_array['type'] == args['type']:
                                    type_array.append(get_type_data_array)
            return jsonify({'results': type_array})

@app.route('/api/v1.0/query_more')
@auth.login_required
def query_more():
    parser = reqparse.RequestParser()
    parser.add_argument('date', required=True, help= 'Required, Invalid Date Input')
    parser.add_argument('regions', type=list, location='json', help= 'Invalid Reggions Input')
    parser.add_argument('types', help= 'Invalid Type Input')
    args = parser.parse_args()

    if args['date']==None:
        return jsonify(date=args['date'],regions=args['regions'])
    else:
        if args['regions']==None and args['types']==None:
            return json_util.dumps(collection.find({'date':args['date']}))
        if args['types']==None:
            return json_util.dumps(collection.find({'date':args['date'], 'regions.region': {'$all': args['regions']}}))
        if args['date']!=None and args['regions']!=None and args['types']!=None:
            regions_more_q = collection.find({'date':args['date'],'regions.region': {'$all': args['regions']},'regions.instanceTypes.type': {'$all': args['types']}})
            return json_util.dumps(regions_more_q)
        else:
            return jsonify({'results': 'Input Error, Try again'})
            
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

