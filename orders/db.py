import abc
import time

from asyncio import sleep
# from sanic.log import logger as log

from orders.log import getCustomLogger
from orders.domain.order import Repository


log = getCustomLogger(__name__)


class MongoDBClient(Repository):
    def __init__(self, host, port, name, user='', password='', *args, **kwargs):
        self._host = host
        self._port = port
        self._name = name
        self._user = user
        self._password = password
        self._args = args
        self._kwargs = kwargs
    
    async def setup(self):
        # mimic setting up time by sleeping asynchronously for 1 seconds
        await sleep(1)
        log.info('Mongodb connection established')
    
    async def close(self):
        # mimic closing of the mongodb client connection
        await sleep(1)
        log.info('Mongodb connection closed')

    async def findByID(self, uID):
        # mimic setting up time by sleeping asynchronously for half second
        await sleep(0.5)
        # return a dummyOjbect for time beign
        dummyObject = {
            'id': int(time.time()*1000),
            'value': 'dummyValue'
        }
        return dummyObject
    
    async def store(self, objToStore):
        log.debug("MongoDBClient.store: objToStore: {}".format(objToStore))
        # mimic setting up time by sleeping asynchronously for half second
        await sleep(0.5)
        # update the transactionID to mimic something has been saved
        if not objToStore.transactionID:
            objToStore.transactionID = int(time.time()*1000)

        return objToStore



    
    



        
