import requests
from random import randint
import json

class RouteYou_Json_Client:
    key = None
    def __init__(self, service, version, timeout = 10, token = None):
        self.url = 'http://api.routeyou.com/%version%/json/%service%/%session%/worker'
        self.key = RouteYou_Json_Client.key
        self.token = token
        
        self._service = service
        self._version = version
        self._timeout = timeout
        
        self._needsToken = True
        self._httpClient = None
    def __getattr__(self, name):
        #magic function to call methods in RouteYou webservice
        def wrapper(*args, **kwargs):
            return self._execurteCall(name, args)
        return wrapper
    def _getHttpClient(self):
        self.url = self.url.replace('%service%',self._service)
        self.url = self.url.replace('%version%',self._version)
        if self.token is None:
            self.url = self.url.replace('%session%','k-' + self.key)
        else:
            self.url = self.url.replace('%session%',self.token)
    def _execurteCall(self, method, params, retry = False):
        self._getHttpClient()
        id = randint(1,1000) 
        data = {
            'jsonrpc' : self._version,
            'id' : id,
            'method' : method,
            'params' : params
            }     
        req = requests.post(self.url, json.dumps(data))
        response = req.json()
        if req.status_code == 200:
            return response
        else:
            print (req.status_code)
            return False
    def getKey(self):
        return self.key

RouteYou_Json_Client.key = 'your_key_here'
#example call to route webservice 2.0
routeService = RouteYou_Json_Client('Route', '2.0')
print(routeService.getFull(381735, 'nl'))