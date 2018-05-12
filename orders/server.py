from asyncio import sleep
from aiohttp import ClientSession
from sanic import Sanic
# from sanic.log import logger as log

from orders.log import getCustomLogger
from orders.routes import addRoutes
from orders.usecases.transact import TransactionProcessor, TransactionValidator
from orders.usecases.fraudcheck import ExternalFraudChecker, InProcessFraudChecker
from orders.usecases.alert import (
    ExternalServiceAlertSender, InProcessAlertSender, MessageBrokerAlertSender
)
from orders.gateway import HTTPTransportGateway, RabbitMqTransportGateway
from orders.mongodb_client import DummyMongoDBClient
from orders.rabbitmq_client import AioPikaClient

app = Sanic('orders', configure_logging=True)

log = getCustomLogger(__name__)


async def setupDB(host, port, name, user, password):
    log.info("Setting up DB")
    db = DummyMongoDBClient(host, port, name, user, password)
    await db.setup()
    return db


def getTransactionInteractor(app):
    """Initialize all the moving parts, this is the place for all
    the Dependency Injection.
    """

    # instantiate the type of transport gateway that would be used to
    # send request/communicate with external alert service, external fraud checking service, etc.
    # alertSenderGateway = HTTPTransportGateway(
    #     client=app.HTTPClient,
    #     host=app.config.ALERT_SENDER_SERVICE_HOST,
    #     uri=app.config.ALERT_SENDER_SERVICE_URI,
    #     method='POST'
    # )
    alertSenderGateway = RabbitMqTransportGateway(
        rabbitMqClient=app.MessageBrokerClient,
        exchange='dummy-exchange',
        routing_key='dummy-alerts',
        options={
            'set_qos': 1,
            'exchangeType': 'topic',
            'queueDurable': True,
            'bindingKey': 'dummy-alerts',
            'deliverMode': 'persistent'
        }
    )
    fraudCheckerGateway = HTTPTransportGateway(
        client=app.HTTPClient,
        host=app.config.FRAUD_CHECKER_SERVICE_HOST,
        uri=app.config.FRAUD_CHECKER_SERVICE_URI,
        method='POST'
    )

    # instantiate the alert sender
    alertSender = InProcessAlertSender()
    #alertSender = ExternalServiceAlertSender(gateway=alertSenderGateway)
    alertSender = MessageBrokerAlertSender(messageGateway=alertSenderGateway)

    # instantiate the fraud checker (could also have been the InProcessFraudChecker )
    # fraudChecker = InProcessFraudChecker()
    fraudChecker = ExternalFraudChecker(gateway=fraudCheckerGateway)
    # create the transaction interactor
    return TransactionProcessor(
        transactionRepo=app.DB,
	    validator=TransactionValidator(),                
	    fraudChecker=fraudChecker,             
	    alerter=alertSender
    )


def setupAiohttpClientSession(loop):
    return ClientSession(loop=loop)

async def setupMessageBroker(app, loop):
    client = AioPikaClient(
        username=app.config.MESSAGE_BROKER_SERVICE_USERNAME,
        password=app.config.MESSAGE_BROKER_SERVICE_PASSWORD,
        host=app.config.MESSAGE_BROKER_SERVICE_HOST,
        port=int(app.config.MESSAGE_BROKER_SERVICE_PORT),
        virtualhoat=app.config.MESSAGE_BROKER_SERVICE_VIRTUALHOST,
        loop=loop
    )
    
    # setup the connection and channel that will be used across the app
    log.info("Setting up Message Broker...")
    await client.setup()
    return client

@app.listener('before_server_start')
async def before_start(app, loop):
    # add the api routes
    addRoutes(app)
    # first add async http client to the app using aiohttp
    app.HTTPClient = setupAiohttpClientSession(loop)
    # now setup the DB connections
    app.DB = await setupDB(
        app.config.DB_HOST, int(app.config.DB_PORT), app.config.DB_NAME,
        app.config.DB_USER, app.config.DB_PASSWORD
    )
    # get the message broker connection
    app.MessageBrokerClient = await setupMessageBroker(app, loop)
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
    # close the db connection
    log.info("Closing Db connection...")
    await app.DB.close()
    # close the message broker connection
    log.info("Closing message broker connection...")
    await app.MessageBrokerClient.close()


def startServer():
    # app.config.from_envvar('SANIC_APP_ORDERS_SETTINGS')
    app.run(host=app.config.HOST, port=int(app.config.PORT), workers=int(app.config.WORKERS))
        

if __name__ == "__main__":
    startServer()
