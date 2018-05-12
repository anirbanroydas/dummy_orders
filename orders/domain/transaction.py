"""The domain package consists of all the core domain objects of the business/application.

 Domain:
 0. OrderItem - This specifies information about the items which consitute an order
 (for the dummy service, we will consider a very generic item)
 1. Order - This species what an order is, the customer whose order it is, and 
 other details (like order address, order items, order total, discount etc)
 2. Transaction - This places an order for a customer (which makes a customer 
 receive the order), this contain transcation infomration like order, payment details etc
 3. PaymentInfo - This specifies information about Payment Detials involved with 
 the transaction like Paytm, Credit Card payment etc
 4. FraudStatus - Specifies if the Transaction is fraudulent or not

 So by using the **Domain Experts** knowledge and seeing the **Ubiquitous Language**,
 we can derive at some domain objects

 - Value Object - Things whose different instances having same values are identical
 - Entities - Things whose different instance having same values are different
 - Aggregates - A collection of Entities and Value Objects which are having high cohesion
 and it also has a root entinty which is the main source of communicting with the other
 entities in the aggregate, also without the root the othe entities doesn't make sense
 or will never be used directly, in the business use case
 - Services - Things which are not a single entity or aggregrage but provide some kind
 of behaviour or service by using the aggregrates, entities etc.
 - Repository - Thigns which facilitate the access and storage of entities and
 aggregrates (if required).

 The `transaction` module of the domain package consists of all the Ttransaction related
 classes and methods.
 
 This basically creates all the domain object and expose some interfaces
 to use them but doesnt depend on anything outside the domain layer.
"""


import abc
import time


from orders.log import getCustomLogger


log = getCustomLogger(__name__)


# different tranaction statuses
TRANSACTION_PENDING = 11
TRANSACTION_FRAUDULENT = 12
TRANSACTION_ALERT_INITIATED = 13
TRANSACTION_ALERT_ERROR = 14
TRANSACTION_ALERT_DONE = 15
TRANSACTION_PAYMENT_INITIATED = 16
TRANSACTION_PAYMENT_ERROR = 17
TRANSACTION_PAYMENT_COMPLETE = 18

TransactionStatus = {
    11 : "TRANSACTION_PENDING",
    12 : "TRANSACTION_FRAUDULENT",
    13 : "TRANSACTION_ALERT_INITIATED",
    14 : "TRANSACTION_ALERT_ERROR",
    15 : "TRANSACTION_ALERT_DONE",
    16 : "TRANSACTION_PAYMENT_INITIATED",
    17 : "TRANSACTION_PAYMENT_ERROR",
    18 : "TRANSACTION_PAYMENT_COMPLETE"
}


class Transaction(object):
    """An aggregrate domain object which constitute the Order on which 
    a Transaction is taking place along with information regarding the
    payment method with its pyament info like debit card, paytm wallet info
    etc.
    """
    
    def __init__(self, order, paymentMethod, payment):
        self._transactionID = int(time.time()*1000)
        self._userID = int(time.time()*1000)
        self._order = order
        self._paymentMethod = paymentMethod
        self._payment = payment
        self._status = TRANSACTION_PENDING
        self._fraudStatus = False
        self._transactionStartTime = int(time.time()*1000)
        self._transactionEndTime = None
    
    def __repr__(self):
        return '{{ Transaction: {{ transactionID: {0}, order: {1}, paymentMethod: {2}, \
            payment: {3}, status: {4}, fraudStatus: {5}, transactionStartTime: {6}, \
            transactionEndTime: {7} }} }}'.format(self._transactionID, self._order,
                self._paymentMethod, self._payment, self._status, self._fraudStatus,
                self._transactionStartTime, self._transactionEndTime)

    def updateFraudStatus(self, fraudStatus):
        self._fraudStatus = fraudStatus
    
    def updateStatus(self, status):
        self._status = status
        
    def updateTransactionEndTime(self):
        self._transactionEndTime = int(time.time()*1000)
    
    @property
    def transactionID(self):
        return self._transactionID
    
    @transactionID.setter
    def transactionID(self, uID):
        self._transactionID = uID
    
    @property
    def paymentMethod(self):
        return self._paymentMethod
    
    @property
    def payment(self):
        return self._payment
    
    @property
    def fraudStatus(self):
        return self._fraudStatus
    
    @property
    def status(self):
        return self._status
    
    def toDict(self):
        return {
            'Transaction': {
                'transactionID': self._transactionID,
                'userID': self._userID,
                'order': self._order,
                'paymentMethod': self._paymentMethod,
                'payment': self._payment,
                'status': self._status,
                'fraudStatus': self._fraudStatus,
                'transactionStartTime': self._transactionStartTime,
                'transactionEndTime': self._transactionEndTime
            }
        }
    
    



