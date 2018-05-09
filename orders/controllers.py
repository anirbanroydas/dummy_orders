from sanic import response
from sanic.exceptions import abort, ServerError, NotFound
#from sanic.log import logger as log

from orders.log import getCustomLogger
from orders.usecases.transact import TransactionRequest
from orders.domain.transaction import TRANSACTION_PAYMENT_COMPLETE, TransactionStatus


log = getCustomLogger(__name__)


async def transactionHandler(req):
    # access the Sanic app isntance
    app = req.app
    # parse request object to receive order, paymentMethod, and payment details
    body = req.json
    if not _isValidTransactionRequest(body):
        log.info("Invalid Transaction Request Body Received: {{ body: {} }}".format(body))
        # raise ServerError("Bad Request", status_code=400)
        return response.json(
            {'message': 'Bad Request'},
            status=400
        )

    resp, hasException = await _processTransaction(app, body)
    if hasException:
        return resp
    return _getTransactionResponse(resp)


#---------------------------------------#
#           Private Methods             #
#---------------------------------------#

def _isValidTransactionRequest(body):
    if 'order' not in body or 'paymentMethod' not in body or (
            'payment' not in body):
        return False
    # for now just chekc for these keyword, for real app, further validator for
    # values inside each of order, pyamentmethod, payment needs to be checked
    # and santized.
    return True


async def _processTransaction(app, body):
    # create TransactionRequest object to be used in the transaction processing usecase
    transReq = TransactionRequest(
        order=body['order'],
	    paymentMethod=body['paymentMethod'],
	    payment=body['payment']
    )
    # use the tranaaction processing interactor to perform the trnasaction usecase
    resp = None
    hasException = False
    try:
        resp = await app.TransInteractor.process(transReq)
        log.debug("transactionHandler: app.TransInteractor.process -> resp: {}".format(resp))
    except Exception:
        # raise ServerError('Something Bad Happened')
        resp = response.json(
            {'message': 'Something Bad Happened'},
            status=500
        )
        hasException = True
        
    return resp, hasException
    
    
def _getTransactionResponse(resp):
    if resp.status != TRANSACTION_PAYMENT_COMPLETE:
        return response.json(
            {
                'message': 'Something Bad Happened',
                'transactionStatus': {
                    'code': resp.status,
                    'status': TransactionStatus[resp.status],
                    'fraudStatus': resp.fraudStatus
                }
            },
            status=500
        )
    # return success response
    return response.json({
        'message': 'Transaction Successfull',
        'transactionID': resp.transactionID
    })
