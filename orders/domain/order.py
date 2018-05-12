"""The order module of the package domain contains all Classes and Methods describing
Order. 

It consists of OrderItem domain entity and Order domain Entity. It also has am
interface definition named Repository.
"""


import abc


class OrderItem(object):
    """A domain entity which specifies the details of individual items which 
    constitutes the full order
    """

    def __init__(self, name, cost, quantity=1, discount=0.0):
        self._itemID = None
        self._name = name
        self._cost = cost
        self._quantity = quantity
        self._discount = discount
    
    def __str__(self):
        return '{{ OrderItem: {{ itemID: {0}, name: {1}, cost: {2}, \
            quantity: {3},discount: {4} }} }}'.format(self._itemID, self._name,
                self._cost, self._quantity, self._discount)
	    

class Order(object):
    """A domain entity which encapsulate information aobut an Order."""
    
    def __init__(self, cost, orderItems=[]):
        self._orderID = None
        self._items = orderItems
        self._cost = cost
    
    def __repr__(self):
        return '{{ Order: {{ orderID: {0}, cost: {1}, items: {2} }} }}'.format(self._orderID, self._cost,
                self._items)


# Inteface
class Repository(metaclass=abc.ABCMeta):
    """Repository exposes the basic interface to store and find domain objects 
    from a repository/store.
    """
    
    @abc.abstractmethod
    async def findByID(self, uID):
        pass
    
    @abc.abstractmethod
    async def store(self, domainObject):
        pass