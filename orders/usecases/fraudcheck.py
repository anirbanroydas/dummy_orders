"""The fraudcheck module of the usecases package consists of all the interfaces and
classes the describe the fraud checking methods.

It has a FraudChecker interface which other concrete FraudCheckers like InProcessAlertSender,
ExternalFraudChecker, etc implement.

This package also consists of all those concrete FraudCheckers implementations mentioned
above.
"""


import abc
import random

from asyncio import sleep

from orders.log import getCustomLogger


log = getCustomLogger(__name__)


# Interface
class FraudChecker(metaclass=abc.ABCMeta):
    """This is an interface which exposes an isFraud method which
    actual FraudChecker implementor should implement and add custom logic to it.

    For example there can be a transaction fraud, there can be order related fraud, etc.
	"""

    @abc.abstractmethod
    async def isFraud(self, transactionObj):
        """This method takes in a obj whose fraudulency is to be checked.

        This method should perform all custom logic, call other services, api calls,
        etc. depending on the use case and return True or False accordingly.
        """
        pass

        
class InProcessFraudChecker(FraudChecker):
    """This is a sample in pocesss fraud chekcer which does not
    communicate with any other external service.
    """

    async def isFraud(self, transaction):
        """Returns True/False randomly beacuse it is a dummy service implementation.

        To make thins interesting, this method sleeps for some seconds to mimic the actual
        behavior as checking if the transaction if fraudulent or not may not be so trivial
        and may take some computational time. Also it may need to access other services or
        databases to take some history of previous transactions etc. Hence the randome sleep
        time
        """

        # sleep anything between 1-2 secs randomly
        await sleep(random.uniform(0.1, 1))

        # choose a random number and return Flase when the number is divisible by 3
        # This is to return True 2/3rd of the time and return False 1/4th of the time
        # but still keeping the random behaviour
        num = random.randint(1, 1000)
        if num % 51 == 0:
            return False
        return True


class ExternalFraudChecker(FraudChecker):
    """Requests an external Fraud Checking Service for the fraudulency of a Transaction.
    This implements the FraudChecker Interface
    """

    def __init__(self, gateway):
        self._gateway = gateway

    async def isFraud(self, transaction):
        """Takes an transaction object as input and sends an appropriate
        request to some external service and get a response from the service as
        to whether the transaction is fraudulent or not using the gateway.
        """

        # first create the appropriate message(post body) that needs to be sent accordingly via the gateway
        transMsg = self._createTransactionMessage(transaction)
        # send the transMsg via the gateway using its send method
        resp = None
        try:
            # receive the response and send if the response sent is True or False by the external
            # Fraud Checking Service
            resp = await self._gateway.send(transMsg)
        except Exception as exc:
            # Log and raise error
            raise exc
        # successful response
        if ('code' in resp and resp['code'] != 200) or (
                'message' in resp and 'isFraud' not in resp['message']):
            raise Exception("Fraud Checker Service returned some error \
                or mismatched response, resp: {}".format(resp))
        
        return resp['message']['isFraud']
    
    #---------------------------------------#
    #           Private Methods             #
    #---------------------------------------#
    
    def _createTransactionMessage(self, transaction):
        transactionObj = transaction.toDict()
        return transactionObj['Transaction']
