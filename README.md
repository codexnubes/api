# Python REST API - AWS Spot Data

Python REST API to get AWS hourly spot instance prices.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

To start API you will need to have python modules installed in virtual environment (Rec).

```
cd ec2-api
rm -rf flask
virtualenv flask
flask/bin/pip install flask
flask/bin/pip install flask_restful
flask/bin/pip install flask_httpauth
flask/bin/pip install pymongo
flask/bin/pip install redis
```

### Installing

Update mongodb and redis connections,

```
client = MongoClient('mongodb://ec2-52-33-101-11.us-west-2.compute.amazonaws.com:27017')
db = client['spot']
collection = db['spotinstance']
```

```
host='127.0.0.1',
port=6379,
password='kiFYmWZB8F'
```

run application,

```
cd ec2-api
./app.py
```

## Running the tests

check the system with,
http://localhost:5000

hit to the endpoints as per the home page.

## Built With

* [Flask](https://github.com/pallets/flask) - The web framework used
* [Mongo](https://www.mongodb.com/) - Database
* [Redis](https://redis.io/) - Caching
