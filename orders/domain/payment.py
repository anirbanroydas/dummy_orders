import abc
import random
from asyncio import sleep

#from sanic.log import logger as log

from orders.log import getCustomLogger


log = getCustomLogger(__name__)


# Interface
class PaymentProcessor(metaclass=abc.ABCMeta):
    """An inteface which constitutes of method that different payment type involved 
    in a Transaction must implement
    
    For example, it can be a Debit Card Payment, it can be Paytm Wallet Payment,
    etc, and each of those payment type will. The reason for keeping PyamentInfo as
    an interface is to allow different Payment options to be used.
    """

    @abc.abstractmethod
    async def pay(self, payment):
        pass


class PaytmPayment(object):
    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs


class ICICIDebitPayment(object):
    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs


class AcceptAllPayment(object):
    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs


class PaytmPaymentProcessor(PaymentProcessor):
    async def pay(self, payment):
        # mimic false payment
        log.info("Starting Paytm payment process...")
        await sleep(random.uniform(0.05, 0.5))
        log.info("Payment Done")
        return True


class ICICIDebitPaymentProcessor(PaymentProcessor):
    async def pay(self, payment):
        # mimic false payment
        log.info("Starting Icici debit payment process...")
        await sleep(random.uniform(0.05, 0.5))
        log.info("Payment Done")
        return True


class AcceptAllPaymentProcessor(PaymentProcessor):
    async def pay(self, payment):
        # mimic false payment
        log.info("Starting generic payment process...")
        await sleep(random.uniform(0.05, 0.5))
        log.info("Payment Done")
        return True


# Facotry method
def getPaymentProcessor(paymentMethod):
    if paymentMethod == 'paytm':
        return PaytmPaymentProcessor()
    elif paymentMethod == 'icici-debit':
        return ICICIDebitPaymentProcessor()
    else:
        return AcceptAllPaymentProcessor()