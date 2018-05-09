dummy-orders
=============

A sample microservice in python for implementing a dummy orders service which processes transactions, alerts if there is a fraudulent transation

Documentation
--------------

**Link :** http://dummy-orders.readthedocs.io/en/latest/


Details
--------

:Author: Anirban Roy Das
:Email: anirban.nick@gmail.com
:Copyright(C): 2018, Anirban Roy Das <anirban.nick@gmail.com>

Check ``dummy-orders/LICENSE`` file for full Copyright notice.


Overview
---------

A sample *microservice* written in python for implementing a **dummy orders** service which processes **transactions** by doing some **payment** and **alerts** if 
there is a **fraudulent** transation.

This uses `Sanic <sanic.readthedocs.io/>`_, for web server and `aio-pika <aio-pika.readthedocs.io/>`_ for connecting to *RabbitMQ* to make alerts asynchronous.

Technical Specs
----------------

:python 3.6: Python Language (Cpython)
:Sanic: Asynchronous uvloop based web framework(faster than tornado and close to some go web frameworks).
:aio-pika: Asyncio based AMQP library which is a wrapper for the Pika library.
:pytest: Python testing library and test runner with awesome test discobery
:pytest-asyncio: Pytest plugin for asyncio lib, to test sanic apps using pytest library.
:Uber\'s Test-Double: Test Double library for python, a good alternative to the `mock <https://github.com/testing-cabal/mock>`_ library
:Docker: A containerization tool for better devops


Features
---------

* Web App 
* microservice
* Sanic App (Async server)
* Alerting
* RabbitMq
