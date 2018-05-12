"""The alert module of the usecases package consists of all the interfaces and
classes the describe the alert sending methods.

It has an AlertSender interface which other concrete AlertSenders like InProcessAlertSender,
MessageBrokerAlertSender, ExternalServiceAlertSEnder, etc implement.

This package also consists of all those concrete AlertSender implementation mentioned
above.
"""


import abc
import random

from asyncio import sleep
# from sanic.log import logger as log

from orders.log import getCustomLogger


log = getCustomLogger(__name__)


# Interface
class AlertSender(metaclass=abc.ABCMeta):
    """Interface that exposes the send method which needs to implemented
    which will send alert asynchronously.

    Example there can be different alert sender, like InProcessAlertSender
    which send alert from this process itself or there can be an ExternalAlertSender
    which takes an alertobject, an external alerting service and requests that service
    to send alerts. There can even be a possibility that implementations and requirement
    may change for the alertSender, hence having an interface helps in keeping
    the Single Responsibility Principle and other SOLID principles intact.
    """

    @abc.abstractmethod
    async def send(self, alertObject):
        """Takes a fraudulent transaction transReq object as input
        and sends it to the alerter service asynchronously.
        """

        pass


class InProcessAlertSender(metaclass=abc.ABCMeta):
    """This is a sample in pocesss alert sender which does not
    communicate with any other external service.
    """

    def __init__(self, alertTo=None):
        self._alertTo = alertTo
    
    async def send(self, alertObject):
        """Takes a alert object as input
        and sends it to the alerter service asynchronously.
        """

        # mimic a dummy sending alert by sleeping for few seonds
        log.info("Sending alert...")
        # sleep for ~1 second to mimic asynchronous alert message sending
        await sleep(random.uniform(0.05, 0.5))
        log.info("Alert Message sent successfully")
    


class MessageBrokerAlertSender(AlertSender):
    """This alertSender sends message via some message broker
    using a message gateway dependency injected into the constructor.
    """

    def __init__(self, messageGateway):
        self._messageGateway = messageGateway

    async def send(self, alertObject):
        """Takes an alert object object as input and sends an appropriate
        alert message to a message broker asynchronously using the 
        gateway(can be http, can be gRpc, amqp client, etc) 
        to a message broker like RabbitMQ or Kafka.
        """

        # first create the appropriate message(post body) that needs to be sent according via the gateway
        alertMsg = self._createAlertMessage(alertObject)
        # send the alertMsg via the gateway using its send method
        try:
            # not saving the response beacuse this is primarily a notification which doens't need to
            # check the response, if response if bad, the exception which will be raised will be caught and
            # handled accordingly
            await self._messageGateway.send(alertMsg)
        except Exception as exc:
            # Log and raise error
            raise exc
    
    #---------------------------------------#
    #           Private Methods             #
    #---------------------------------------#

    def _createAlertMessage(self, alertObject):
        alertDict = alertObject.toDict()
        alertMsg = {
            'alertTypes': ['sms', 'email'],
            'message': alertDict
        }
        return alertMsg


class ExternalServiceAlertSender(AlertSender):
    """This alertSender sends message via some external service
    using some external gateway(http client, grpc cleint etc) that
    is dependency injected into the constructor.
    """

    def __init__(self, gateway):
        self._gateway = gateway

    async def send(self, alertObject):
        """Takes an alert object object as input and sends an appropriate
        alert message to a the external service using the gateway.
        """

        # first create the appropriate message(post body) that needs to be sent according via the gateway
        alertMsg = self._createAlertMessage(alertObject)
        # send the alertMsg via the gateway using its send method
        try:
            # not saving the response beacuse this is primarily a notification which doens't need to
            # check the response, if response if bad, the exception which will be raised will be caught and
            # handled accordingly
            await self._gateway.send(alertMsg)
        except Exception as exc:
            # Log and raise error
            raise exc
    
    #---------------------------------------#
    #           Private Methods             #
    #---------------------------------------#

    def _createAlertMessage(self, alertObject):
        # for now send the alertObject as it is, for real app, there may be some additional data
        # taht may be addeed
        return alertObject.toDict()

