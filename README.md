EC2 Rest API

###Startup Instructions
01. ```cd ec2-api```
02. ```rm -rf flask```
03. ```virtualenv flask```
04. ```flask/bin/pip install flask```
05. ```flask/bin/pip install flask_restful```
06. ```flask/bin/pip install flask_httpauth```
07. ```flask/bin/pip install pymongo```

###Update Database Config
```client = MongoClient('mongodb://ds153978179.mlab.com:53179/')```
```db = client['ec2-api']```
```db.authenticate('test','gvh5678')```
```collection = db['data']```

###Run API
```./app.py```