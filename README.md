## Client Server

Make sure Client.py and Server.py are executable:

```
chmod +x Client.py
chmod +x Server.py
```

To run each file, you need to get your own ip address. I have a function [here](helpers.py) that tells you what your IP is and then fill in info as appropriate.

Edit [config.py](config.py) and add your own info. I created this so I wouldn't have to type in the params everytime.

Here is my config:

```
database = "stockgame"
host = "192.168.1.177"
port = 6000
debug = False
```

I was using the `debug` value to add debug info to my classes. By putting `import config` you now have variables = to the values in the file. So you could do things like: 

```python
if debug == True:
    print("Some debug statement")
```

### Starting the Server

**Method 1**

Usage: `./Server.py host=<your.ip.address> <port=XXXX> <db=DBNAME>`

```bash
./Server.py host=192.168.0.1 port=6000 db=stockgame
```

**Method 2**

Usage: `./Server.py`

This will work if your config.py is edited correctly.


### Using the Client

The client is where your requests come from. Here are some examples:

**Command:**
```bash
./Client.py action=searchkey collection=info key=Symbol value=GOOG
```

**Result:**
```
{'results': {'success': True, 'count': 1, 'data': [{'_id': 'GOOG', 'Symbol': 'GOOG', 'Company': 'Alphabet Inc Class C', 'Name': 'GOOG', 'Sector': 'Information Technology', 'SECFilings': 'http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=GOOG'}]}}
```

**Command:**
```bash
./Client.py action=search collection=data_med params='{"Symbol":"GOOG","Year":2018}'
```

**Result:**
```
{'results': {'success': True, 'count': 251, 'data': [{'_id': '5e72a5881c54daa33e017e00', 'Date': '2018-01-02T12:00:00', 'Open': 1048.34, 'High': 1066.94, 'Low': 1045.23, 'Close': 1065.0, 'Volume': '1237600', 'Symbol': 'GOOG', 'AdjClose': 1065.0, 'Name': 'GOOG-2018-01-02', 'Year': 2018, 'Month': 1}, {'_id': '5e72a5881c54daa33e017e01', 'Date': '2018-01-03T12:00:00', 'Open': 1064.31, 'High': 1086.29, 'Low': 1063.21, 'Close': 1082.48, 'Volume': '1430200', 'Symbol': 'GOOG', 'AdjClose': 1082.48, 'Name': 'GOOG-2018-01-03', 'Year': 2018, 'Month': 1},
...
...
...
{'_id': '5e72a5881c54daa33e017efa', 'Date': '2018-12-31T12:00:00', 'Open': 1050.96, 'High': 1052.7, 'Low': 1023.59, 'Close': 1035.61, 'Volume': '1493300', 'Symbol': 'GOOG', 'AdjClose': 1035.61, 'Name': 'GOOG-2018-12-31', 'Year': 2018, 'Month': 12}]}}
```

**Command:**
```bash
./Client.py action=insert collection=temporary data='{"stock":"GOOG","price":1000.88,"date":"13 Jan 2018"}'
```

**Result:**
```
{'results': {'success': True, 'result_id': '5e73fa94fc8b895deddff0dc', 'message': 'Inserted 1 item into temporary'}}
```

