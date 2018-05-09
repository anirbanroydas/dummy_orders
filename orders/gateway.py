import abc

import aiohttp


class TransportGateway(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    async def send(self, msgToSend):
        pass


class HTTPTransportGateway(TransportGateway):
    def __init__(self, client, host, uri, method, *args, **kwargs):
        self._client = client
        self._host = host
        self._uri = uri
        self._method = method
        self._args = args
        self._kwargs = kwargs
    
    async def send(self, msgToSend):
        # perform the aiohttp http client request her
        # a POST request
        url = '{}{}'.format(self._host, self._uri)
        async with self._client.post(url, json=msgToSend, timeout=60) as resp:
            return await resp.json()


    
    



        
