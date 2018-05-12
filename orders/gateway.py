"""The gateway module acts as an interface the infrastructure can use to
perform the usecases. This consists of all interfaces, concrete implementations of
those interfaces which help in communicated to external services.
"""

import abc

import aiohttp

from orders.log import getCustomLogger


log = getCustomLogger(__name__)


class TransportGateway(metaclass=abc.ABCMeta):
    """This interface exposes a send method which other concrete
    TransportGateway needs to implement.

    The TransaportGateway exposes a method which is used by different
    usecases to talk/communicate/send some data to some external service.
    It can be an Http service, message broker service, etc, which implements
    this interface.
    """

    @abc.abstractmethod
    async def send(self, msgToSend):
        """Sends the msgToSend to some service via some logic which the
        actual concrete implementers write.
        """

        pass


class HTTPTransportGateway(TransportGateway):
    """This implements the TransportGateway and accepts some http client
    and other http related details as dependecies. This transport gateway
    is for talking via the http protocol.
    """
    
    def __init__(self, client, host, uri, method, *args, **kwargs):
        self._client = client
        self._host = host
        self._uri = uri
        self._method = method
        self._args = args
        self._kwargs = kwargs
    
    async def send(self, msgToSend):
        """Uses some client which is dependency inject to send the msg via
        http protocol.
        """

        # perform the aiohttp http client request her
        # a POST request
        url = 'http://{}{}'.format(self._host, self._uri)
        try:
            async with self._client.post(url, json=msgToSend, timeout=60) as resp:
                return await resp.json()
        except Exception as exc:
            log.error("HTTPTransportGateway's self._client.post \
                raised exception for: {{ url: {}, json: {}, \
                exc: {} }}".format(url, msgToSend, exc))
            raise exc


class RabbitMqTransportGateway(TransportGateway):
    """This implements the TransportGateway and accepts some rabbitmq client
    and other rabbitmq related details as dependecies. This transport gateway
    is for talking via the amqp protocol to rabbitmq.
    """
    
    def __init__(self, rabbitMqClient, exchange='default_exchange',
            routing_key='', options=None):
        self._rabbitMqClient = rabbitMqClient
        self._exchange = exchange
        self._routing_key = routing_key
        self._options = options
    
    async def send(self, msgToSend):
        """This uses the rabbitmqclient of the class to send the msg usign the rabbitmqclient's
        publish method.
        """

        try:
            await self._rabbitMqClient.publish(
                msgToSend, self._exchange,
                self._routing_key, self._options
            )
        except Exception as exc:
            log.error("RabbitMqTransportGateway's self._rabbitMqClient.publish \
                raised exception for: {{ msgToSend: {}, exchange: {}, \
                routing_key: {}, options: {}, exc: {} }}".format(
                    msgToSend, self._exchange, self._routing_key,
                    self._options, exc
                )
            )
            raise exc



    
