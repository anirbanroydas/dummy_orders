from asyncio import sleep
from aiohttp import ClientSession
from sanic import Sanic
# from sanic.log import logger as log

from orders.log import getCustomLogger
from orders.routes import addRoutes
from orders.usecases.transact import TransactionProcessor, TransactionValidator
from orders.usecases.fraudcheck import ExternalFraudChecker, InProcessFraudChecker
from orders.usecases.alert import ExternalAlertSender, InProcessAlertSender
from orders.gateway import HTTPTransportGateway
from orders.db import MongoDBClient

app = Sanic('orders', configure_logging=True)

log = getCustomLogger(__name__)


async def setupDB(host, port, name, user, password):
    log.info("Setting up DB")
    db = MongoDBClient(host, port, name, user, password)
    await db.setup()
    return db


def getTransactionInteractor(app):
    """Initialize all the moving parts, this is the place for all
    the Dependency Injection.
    """

    # instantiate the type of transport gateway that would be used to
    # send request/communicate with external alert service, external fraud checking service, etc.
    alertSenderGateway = HTTPTransportGateway(
        client=app.HTTPClient,
        host=app.config.ALERT_SENDER_SERVICE_HOST,
        uri=app.config.ALERT_SENDER_SERVICE_URI,
        method='POST'
    )
    fraudCheckerGateway = HTTPTransportGateway(
        client=app.HTTPClient,
        host=app.config.FRAUD_CHECKER_SERVICE_HOST,
        uri=app.config.FRAUD_CHECKER_SERVICE_URI,
        method='POST'
    )
    # instantiate the alert sender
    alertSender = InProcessAlertSender()
    #alertSender = ExternalAlertSender(gateway=alertSenderGateway)
    # instantiate the fraud checker (could also have been the InProcessFraudChecker )
    fraudChecker = InProcessFraudChecker()
    #fraudChecker = ExternalFraudChecker(gateway=fraudCheckerGateway)
    # create the transaction interactor
    return TransactionProcessor(
        transactionRepo=app.DB,
	    validator=TransactionValidator(),                
	    fraudChecker=fraudChecker,             
	    alerter=alertSender
    )


def setupAiohttpClientSession(loop):
    return ClientSession(loop=loop)
    

@app.listener('before_server_start')
async def before_start(app, loop):
    # first add async http client to the app using aiohttp
    app.HTTPClient = setupAiohttpClientSession(loop)
    # now setup the DB connections
    app.DB = await setupDB(app.config.DB_HOST, app.config.DB_PORT,
        app.config.DB_NAME, app.config.DB_USER, app.config.DB_PASSWORD)
    # add the api routes
    addRoutes(app)
    # get the usecase interactors here, so that app can use the interactors
    # to perform the usecases, here get/create the transaction specific interactor
    app.TransInteractor = getTransactionInteractor(app)
    log.info('Starting server on http://{}:{}'.format(app.config.HOST, app.config.PORT))


@app.listener('after_server_start')
async def after_start(app, loop):
    log.info("\nServer Started.\n")


@app.listener('before_server_stop')
async def before_stop(app, loop):
    log.info("Stopping Server....")


@app.listener('after_server_stop')
async def after_stop(app, loop):
    await app.DB.close()


def startServer():
    app.config.from_envvar('SANIC_APP_ORDERS_SETTINGS')
    app.run(host=app.config.HOST, port=app.config.PORT, workers=app.config.WORKERS)
        

if __name__ == "__main__":
    startServer()
