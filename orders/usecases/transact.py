"""The usecases module consists of all the usecases of the business/application.

Use Case:
0. Process Order
1. Process Transaction
2. Check Transaction for Fraud
3. Save Transaction
4. Alert/Notify when Fraudulent Transaction

Thus, the usecases package basically creates all the use cases and exposes 
some interfaces to use them but doesnt depend on anything outside the usecases layer.

The transact module of the usecases package consists of all the interfaces and
classes the describe the transaction processing methods.

It has a TransactionProcessor class which takes in different usecase interactors as
dependencies and takes in and processes a transaction of type TransactionRequest.

This package also consists Validator interface which other concrete TransactionValidator etc
implements which validates a TransactionRequest object.
"""


import abc

#from sanic.log import logger as log

from orders.log import getCustomLogger
from orders.domain.transaction import Transaction
from orders.domain.payment import getPaymentProcessor
from orders.domain.transaction import (
    TRANSACTION_PENDING, TRANSACTION_FRAUDULENT, TRANSACTION_ALERT_INITIATED,
    TRANSACTION_ALERT_ERROR, TRANSACTION_ALERT_DONE, TRANSACTION_PAYMENT_INITIATED,
    TRANSACTION_PAYMENT_ERROR, TRANSACTION_PAYMENT_COMPLETE
)


log = getCustomLogger(__name__)


class TransactionRequest(object):
    """This a data which is passed to the TransactionProcessor service 
    doTransaction method
    """

    def __init__(self, order, paymentMethod, payment):
	    self.order = order
	    self.paymentMethod = paymentMethod
	    self.payment = payment


class TransactionProcessor(object):
    """This is a usecase interactor service which takes in other interactor services
	as dependencies injected and exposes methods to process/validate a transaction.
	"""

    def __init__(self, transactionRepo, validator, fraudChecker, alerter):
	    self._transactionRepo = transactionRepo
	    self._validator = validator                   
	    self._fraudChecker = fraudChecker                  
	    self._alerter = alerter


    async def process(self, transReq):
        """This method takes in a TransactionRequest object as 
        input and creates a domain level Transaction object and saves it
		to the repository.
        
        It also checks if the transaction is fraudulent or not and sends
		an alert if it is fraudulent.
        """

        # step 1:  validate the Transaction Request -> Order, PaymentMethod, PaymentInfo
        isValid = self._validator.validate(transReq)
        if not isValid:
            raise Exception("TransactionValidator returned invalid for {{ TransactionRequest: \
                object: {} }}".format(transReq))
        # step 2: Create new domain Transaction ojbect with fraud status false and transaction status pending
        transaction = self._createTransaction(transReq)
        try:
            await self._fraudCheck(transaction)
            # save trnsaction to Db so that if payment processing fails, we will have some transaction data
            # db to check for pending statuses
            await self._saveTransaction(transaction)
            # save transction raise exception, payment processing will not proceed
            await self._processPayment(transaction)
            # if process payment is successfully done, then go and update the tranasction in DB
            await self._saveTransaction(transaction)
        except Exception:
            return transaction
        return transaction

    #---------------------------------------#
    #           Private Methods             #
    #---------------------------------------#

    async def _fraudCheck(self, transaction):
        isFraud = False
        try:
            isFraud = await self._fraudChecker.isFraud(transaction)
        except Exception as exc:
            log.error("FraudChecker.isFraud raised exception for: {{ transactionID: {}, \
                exc: {} }}".format(transaction.transactionID, exc))
            raise exc
        else:
            if isFraud:
                log.info("Found Fraudulent Transaction: {{ transactionID: {} }}".format(transaction.transactionID))
                transaction.updateFraudStatus(True)
                transaction.updateStatus(TRANSACTION_FRAUDULENT)
                try:
                    await self._raiseAlert(transaction)
                except Exception as e:
                    raise e
                raise Exception("FraudulentTransaction")
   
    async def _raiseAlert(self, transaction):
        try:
            transaction.updateStatus(TRANSACTION_ALERT_INITIATED)
            await self._alerter.send(transaction)
            transaction.updateStatus(TRANSACTION_ALERT_DONE)
        except Exception as exc:
            transaction.updateStatus(TRANSACTION_ALERT_ERROR)
            log.error("AlertSender.send raised exception for: {{ transactionID: {}, \
                exc: {} }}".format(transaction.transactionID, exc))
            raise exc
    
    async def _processPayment(self, transaction):
        paymentMethod = transaction.paymentMethod
        payment = transaction.payment
        try:
            paymentProcessor = getPaymentProcessor(paymentMethod)
            transaction.updateStatus(TRANSACTION_PAYMENT_INITIATED)
            await paymentProcessor.pay(payment)
            # payment processing is done, update status and transaction end time
            transaction.updateStatus(TRANSACTION_PAYMENT_COMPLETE)
            transaction.updateTransactionEndTime()
        except Exception as exc:
            # payment processing couldn't complete, update just the trnnsaction end time
            transaction.updateStatus(TRANSACTION_PAYMENT_ERROR)
            transaction.updateTransactionEndTime()
            log.error("PaymentProcessor.pay raised exception for: {{ paymentMethod: {}, \
                payment: {}, exc: {} }}".format(paymentMethod, payment, exc))
            raise exc
        
    async def _saveTransaction(self, transaction):
        try:
            await self._transactionRepo.store(transaction)
        except Exception as exc:
            log.error("TransactionRepo.store raised exception for: {{ transactionID: {}, \
                exc: {} }}".format(transaction.transactionID, exc))
            raise exc

    def _createTransaction(self, transReq):
        transaction = Transaction(transReq.order, transReq.paymentMethod, transReq.payment)
        log.debug("New Transaction Created: {}".format(transaction))
        
        return transaction
            

# Interface
class Validator(metaclass=abc.ABCMeta):
    """Interface which other specific validators implements to validate any
    type of request object.
    """

    @abc.abstractmethod
    def validate(self, requestObject):
        """Takes in a request object, validates and returns True or False
        depending on if the object is valid or not
        """
        pass


class TransactionValidator(Validator):
    """Validates a Transaction Request
    
    This implements the Validator Interface having one method called validate.
    """

    # implememnting the validate method of the Validator Interface
    def validate(self, transReq):
        """This method takes in a transaction Request object, and tries
        to validate the request object and returns a boolean whether it is
        valid or not.
        """

        # dummy service -> hence -> validating always by default
        # real service should have a specific validity check based on the actual Transaction object
        return True

