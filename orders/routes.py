import orders.controllers as controllers

def addRoutes(app):
    """Adds routes to Sanic App for different controllers using
    the ``add_route`` method.
    """

    # Add different routes for each of the controllers
    app.add_route(controllers.transactionHandler, '/transact', methods=['POST'])
    # In real app, there will multiple routes, which will be added here one by one
    # This means this one single place to have access to all the routes