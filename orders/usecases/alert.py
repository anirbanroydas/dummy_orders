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


class ExternalAlertSender(AlertSender):
    """Interface that exposes the send method which needs to implemented
    which will send alert asynchronously
    """

    def __init__(self, gateway):
        self._gateway = gateway

    async def send(self, alertObject):
        """Takes a fraudulent transaction object as input
        and sends it to the external service situated at `self._serviceHost`
        asynchronously using the gateway(can be http, can be gRpc can be to a
        message broker like RabbitMQ or Kafka).

        Thus the power of decoupled systems following SOLID principles and
        following somewhat clean architecture.
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
        return alertObject


class InProcessAlertSender(metaclass=abc.ABCMeta):
    def __init__(self, alertTo=None):
        self._alertTo = alertTo
    
    async def send(self, alertObject):
        """Takes a alert object as input
        and sends it to the alerter service asynchronously.
        """

        alertMsg = self._createAlertMessage(alertObject)
        log.info("Sending alert...")
        # sleep for 2 seconds to mimic asynchronous alert message sending
        await sleep(random.uniform(0.05, 0.5))
        log.info("Alert Message sent successfully")
    
    #---------------------------------------#
    #           Private Methods             #
    #---------------------------------------#

    def _createAlertMessage(self, alertObject):
        # for now send the alertObject as it is, for real app, there may be some additional data
        # taht may be addeed
        return alertObject