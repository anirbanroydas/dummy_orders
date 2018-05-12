dummy_orders
=============

A sample microservice in python for implementing a dummy orders service which processes transactions, alerts if there is a fraudulent transation using alertman and fraud_police.

Details
--------

:Author: Anirban Roy Das
:Email: anirban.nick@gmail.com

Features
---------

* microservice
* Asyncio event loop
* Order/Transaction Processing
* RabbitMq
* Alerts by sending events to RabbitMq
* Docker compose setup to create a full service deployment including alertman, fraud_police and rabbitmq

Overview
---------

* **Some Design Specific Note:**

  I have tried to structure the code using `Clean Architecture <https://8thlight.com/blog/uncle-bob/2012/08/13/the-clean-architecture.html>`_ proposed by 
  `Robert Martin <https://en.wikipedia.org/wiki/Robert_C._Martin>`_, famously known as **Uncle Bob**.

  **Clean Architecture** is some better or flavour of other known architectures like `Porst & Adapters <https://spin.atomicobject.com/2013/02/23/ports-adapters-software-architecture/>`_, 
  `The Onion Architecture <http://jeffreypalermo.com/blog/the-onion-architecture-part-1/>`_, etc.

  Clean architecture mainly focusses on following one principle strictly that is **Dependency Inversion**. Keeping all dependencies flow in a uni direction 
  makes it quite quite powerful. Infact, I have finally realized the value of proper **dependency injections** while implementing clean architecture.

  **NOTE :** This is not the best architecture for all usecases and of course a little more verbose and more boilerplate than some other design patterns, but it 
  does help you keep you codebase fully maintainable for the long run. You may not agree with Clean architecture's philosophy sometimes. But I am just using it to understand it more.

  Btw, `Robert Martin`_ is also known for 
  the `S.O.L.I.D <https://medium.com/@cramirez92/s-o-l-i-d-the-first-5-priciples-of-object-oriented-design-with-javascript-790f6ac9b9fa>`_ 
  principles which have shaped real greate design choices when it comes to writing 
  good maintainable **Object Oriented Code**. But, *SOLID* is talked about even in 
  non object oriented langauges like **Golang**.

  **P.S :** Just for motivational purposes, I am implementing few projects in *Clean Architecture* to understand it better and challenge the norm or my own design choices.

  > This is a good talk by the same guy `link to talk <https://www.youtube.com/watch?v=o_TH-Y78tt4>`_


* **Service Details**

  This service is server based microservice which exposes few api. Instead of that it just listens for alert events 
  from a source (in this case, it is `RabbitMQ <https://www.rabbitmq.com/>`_, which for 
  everyone's sake could also be `Redis <https://redis.io/>`_, or `Kafka <https://kafka.apache.org/>`_
  or others.)

  This service is server based sample microservice app, this exposes some rest api, in this sample usecase, just one.
  **dummy_orders** which is pacakged as the name **orders** and hence we will refere to it as orders. I kept the project name
  as dummy_orders instead of orders becasuse a project name as generic as orders was not giving me good feels.
  
  I have tried to mimic much or (may be far less) of what a real world order service will look like. Although I have tried to mimic
  few things, they are kept or used just for demo/dummy purpose which doesnt actually do anything. This will became a little clear 
  once I will explain what I mean a little below.

  A real world Orders service will have things like order, order items, transactions to place those orders, payment processing to
  charge for those orders being placed. Well, in a proper microservcie architecture, transactions may itself be a different microservice, 
  but for simplicity's and sample app's sake, transaction is implemented(rather demonstrated) in this orders service itself.

  In fact, the major part of the dummy service revolves around the transaction aspect itself. This service exposes just the one Api
  ``/trasact`` which is a **POST** api which takes some values as request body in json and processes that dummy transaction.

  Now, just for good design purpose, I have also added a minimilastic Classes for Order, OrderItems and some Payment Methods, which
  actually doesn't do anything but gives the service a real look. When you scout through the code, you may get the purpose why I have added it,
  in nutshell, to emphasis on the benefits of **Clean Architecture** as to how anything can be plugged in without touching anything already coded.

  The main implementation of the Order service revolves around the domain **Transaction** and the usecase **Check Transaction for Fraudulency**. Yes, this dummy 
  service's main task is to take some transaction like objest as request on its exposed ``/transact`` api and process the transaction and return 
  if the transaction is fraudulent or not. There is no real transaction (like payment or anything) which actually takes place. Just randomly return 
  true or false. (well, not so directly either, read on)

  Let me now show you the System Design and Code design. I will show you how the project can be made in 3 different ways (there can be many different system design choices, but 
  I am focussing on 3 of them). 

  Here is the evolving architecture from basic to highly scalable.

  
  **Architecture 1.0**
  

  This is the simplest choice. Have everything in one service.
  - A transaction request comes in to the ``/transact`` api.
  - Process the transaction -> Call in-process(same service) ``isFraud()`` function which randomly returns True/False.
  - Based on the response of the function ``isFraud()``, call an ``alert()`` function which alerts about fraud transaction via email.

  Done!

  **Architecture 2.0**

  This is next step from Architecture 1.0.
  1. A transaction request comes in via the ``/transact`` api.
  2. Process the transaction -> Call in-process(same service) ``isFraud()`` function which randome returns True/False.
  3. Based on teh response of the ``isFraud()`` function, call an ``alert()`` function but does not send email directly.
     
     Here is the change, separate the service which sends alerts.
      
     But the question is why?

     a. Because, it helps scale the transaction servcie better, generally sending emails and other alerts may take some time to do,
        while the transaction service may get hit with high load, at this point of time it is better to do the more computational work, 
        or work which can be offloaded and does not required very immedaite sub second handling to a different service.

        In this way, the transaction service can do its own job properly without any other job which is not its responsibility strictly.
      
     b. The transaction itself takes some time to complete, like checking for fraud, hit payment gateway api etc, at this time if the transaction service
        gets hit with many such requests, at that time it is important to atleast acknowledge those requests and take some time to process them. If we separate the alert sending
        job to a separate service, then the transaction service could take in more load and hand over alerting jobs to some to other service which can do that asynchronously and 
        independently without any involvment of transaction service. This seems like a good place and candidate for creating a new service. Specially because both are independent of each 
        other's request/response event.

     How do we do it?
     
     Now this separate service could be implemented in at least couple of ways.
    
     A. Have a separate alerting service which exposes an HTTP api, which takes an alert request and sends email and responds back to the service which requested it.
            
        This is good and separates the concerns. Only issue is its possible one of the service may become unavailable, if the alerting service in not available not other service can send
        request to alert service to send the alerts. Well, you can solve it by saving the alerts in a Database and have some cron jobs or something process the database for unsent alerts and
        try to send them again until succeed. Apart from this this is a fairly good choice.

     B. Decouple even on this level by having a message broker or message queue, where you send in the alert to be sent independent of whether the service which will actually send the alerts
        is available or not. Hence, transaction service(orders service in this case) is completely independent of the alerting service. Both equally and highly scalable separately.

        The only cost is having another moving part involved, the message broker, like RabbitMq, Kafka or even Redis for that matter. I have used this (using rabbitbq as the message broker) in this project.
  
  4. So, the alert event is sent to RabbitMq at a specific exchange, to specific topic.
  5. Alert processing service (alertman) subscribes (rather consumes as worker from worker queue) to those alert events.

     Many workers can be started (like 1, 5, 10, 100 based on the load, thus scalable) and process those alert events and send alerts like email, sms, etc, again asynchronously since all of them are
     mostly IO bound.
  6. Once the alert event is sent to rabbitmq, just return form orders service immediately without waiting on ther alerts to be sent. The alerting service (alertman) will process them on its own time 
     without being concerned with the orders service. Rabbitmq will keep those alerts which are not processed within the queue to be consumed whenever there is a worker.

  
  **Arhictecture 3**

  .. image:: architecture_3.png

  Well, everything is good, but Architecture 2.0 has one another bottleneck. The bottleneck is the ``isFraud()`` function, well, in this simple case where it only returns True/False, 
  this is not an issue, but real work ``isFraud()`` will do some computational work to check if a transaction is fraudulent or not. This can eat on the transaction service's cpu and time,
  this part can be sent to a different servcie and let the transaction service wait on the network io for the computation to finish, meanwhile it can keep accepting other transact requests, which
  if the isFraud() is in the same process will not be possible because there will be high load on the transaction service already because of those computations.

  Hence, the choice of make the fraud_police service which takes transaction requests from this transaction service and processes it from Fraud or not. Sends the response back to orders servcie.

  Orders servcie which was waiting asynchronously on the fraud chekcing request sent to fraud_police, after receiving the response, sends appropriate response.

  
  **Code Design**

  As mentioned above, I have implemented the project much in a Clean architecture style, so there are domain package, usecases package, gateways, then infrastructure related code, 
  the dependency is in the order infrastructure ->(depends) -> gateway -> (depends on) -> usecases -> (depends one) domain.

  Meaning domain does not depend on anthing, usecases only depend on domain object and nothing above, gateways may depend on usescases or domain but not nothing above, and then infrastrucutre may depend onl anything below.

  To adher to this design, the code structure is also like that. Moreover, to make this possible, something good comes out of it, that is having good interfaces defined, and implement those
  interfaces later. Like fradu processing can be an interface, and there can be different implementation of it which can then be sent down the layer. This also helps in testing and also for this project, 
  like since we need only dummy implementation we can create dummy concrete classes of the interfaces, and the project will still work when we add actual implementation with not change in the 
  actual business or domain logic (one of the gretest power of clean code and SOLID design)

  I have implemented the same code structure in all the 3 associated projects.
  

Technical Specs
----------------

:python 3.6: Python Language (Cpython)
:RabbitMQ: Used for sending in on events of fraud alerts which gets consumed by alertman service to further process those events, all asynchronously.
:aio-pika: Asyncio based asynchronous AMQP library which is a wrapper for the Pika library to talk to RabbitMQ.
:aiohttp: Asyncio event loop based asynchronous http client (a drop down replacement for the famous requests library.
:pytest: Python testing library and test runner with awesome test discobery
:pytest-asyncio: Pytest plugin for asyncio lib, to test sanic apps using pytest library.
:Uber\'s Test-Double: Test Double library for python, a good alternative to the `mock <https://github.com/testing-cabal/mock>`_ library
:Docker: A containerization tool for better devops


Deployment
~~~~~~~~~~~

There are two ways to deploy:

* using `Virtualenv <https://virtualenv.pypa.io/en/stable/>`_
* using `Docker <https://www.docker.com/>`_


Prerequisite 
-------------

* **Required**

  Copy (not move) the ``env`` file in the root project directory to ``.env`` and add/edit 
  the configurations accordingly.

  This needs to be done because the server, or docker deployment, or some script may want some pre configurations like ports, 
  hostnames, etc before it can start the service, or deploy the service or may be to run some scripts.

* **Optional**

  To safegurad secret and confidential data leakage via your git commits to public 
  github repo, check ``git-secrets``.

  This `git secrets <https://github.com/awslabs/git-secrets>`_ project helps in 
  preventing secrete leakage by mistake.


Using Virutalenv
-----------------

There is a ``deploy-virtualenv.sh`` script which does all the **heavylifting** and 
**automates** the entire creation of viratualenv, activating it, installing all 
dependencies from the requirements file and initalizing all environment variables 
required for the service and finally installs the service in the virtualenv.

Check the ``deploy-virtualenv.sh`` file for the actual way if you want to see the steps.
    ::    
    
        $ chmod +x deploy-viratualenv.sh
        $ ./deploy-virtualenv.sh


Using Docker
-------------

* **Step 1:**
    
  Install **docker** and **make** command if you don't have it already.

  * Install Docker
    
    Follow my another github project, where everything related to DevOps and scripts are 
    mentioned along with setting up a development environemt to use Docker is mentioned.

    * Project: https://github.com/anirbanroydas/DevOps

    * Go to setup directory and follow the setup instructions for your own platform, linux/macos

  * Install Make
    ::
            
        # (Mac Os)
        $ brew install automake

        # (Ubuntu)
        $ sudo apt-get update
        $ sudo apt-get install make

* **Step 2:**

  There is ``Makefile`` present in the root project directory using actually hides
  away all the docker commands and other complex commands. So you don't have to actually 
  know the **Docker** commands to run the service via docker. **Make** commands will do the
  job for you.

  * Make sure the ``env`` file has been copied to ``.env`` and necessary configuration changes done.
  * There are only two values that need to be taken care of in the ``Makefile``

    * BRANCH: Change this to whatever branch you are in if making changes and creating the docker images again.
    * COMMIT = Change this to a 6 char hash of the commit value so that the new docker images can be tracked.

  * Run the command to start building new docker image and push it to docker hub.
        
    * There is a script called ``build_tag_push.sh`` which actually does all the job of building the image, tagging the image ans finally pushing it to the repository.
    * Make sure you are logged into to your docker hub acount. 
    * Currently the ``build_tag_push.sh`` scripts pushes the images to ``hub.docker.com/aroyd`` acount. Change the settings in that file if you need to send it to some other place.
    * The script tags the new built docker image with the branch, commit and datetime value.
    * To know more, you can read the ``Dockerfile`` to get idea about the image that gets built on runing this make command.

      ::
        
        $ make build-tag-push

* **Step 3:**

  Pull the image or run the image separately or you can run it along with other services, docker containers etc.
  
  The exact details of how to run all the other services, namely `fraud_police <https://github.com/anirbanroydas/fraud_police>`_, 
  `alertman <https://github.com/anirbanroydas/alertman>`_ and **rabbitMQ** together all in dockerized environment is mentioned 
  below in the Usage section.


Usage
-----

There are 3 services and 1 infrastracture services involved in this project.

1. `orders <https://github.com/anirbanroydas/dummy_orders>`_
2. `alertman`_
3. `fraud_police`_
4. `rabbitmq service <https://hub.docker.com/_/rabbitmq/>`_

**All these services** mean the 3 services/projects apart from the rabbitmq infrastructure service.

All these services have specific ``Dockerfiles`` mentioned in their respective github repos.
All these project also have a ``build_tag_push.sh`` script which you can invoke via ``make`` command mentioned in the ``Makefile`` file.

When the respective projects run the ``make build-tag-push`` command to build and push the lastest docker image to the docker hub repo, a 
new container image for the latest codebase for their respective projects get available in the docker hub repository.

Now to run all these services together in a dockerized environment, you can either run each of them individually using ``docker run`` commands or 
you can use ``docker-compose`` to keep things in one place and documented.

This project(**dummy_orders**), unlike the other 2 projects also contain few extra files, namely the ``docker-compose.yml``. This file contains all the 
deployment related config to make all the 3 services run togehter.

**NOTE:** I could have kept the ``docker-compose.yml`` file in any of the 3 projects, I kept it here because **dummy_orders** project has 
the most dependencies and it felt as the right place.

Also, the ``Makefile`` present in this project, unlike the other 2 projects have extra and verbose commands to do more things because of the addition of the ``docker-compose.yml`` 
file. It has all the deploy as well docker management related commands. All you have to do is run the ``make`` commands insted of the ``docker`` commands. You could still run the ``docker`` 
commands to meet your ends, but ``Makefile`` helps everybody.(with or without docker knowledge).

**Here are the commands you may run in specific order to make things work perfectly.**

* Step a. First make sure the environment files (all ``.env`` files) present in all the 3 projects have been created and settings added.

* Step b. Create a common **docker network** so that each service (dockerized container) can talk/communicate with each other without having to expose different ports etc, to the host machine. Services(these projects in a docker container) can talk to each service directly via the ``docker-compose.yml`` service names.
  ::
      
      $ make build-network-dev


* Steb c. Create a **data volume** so that **rabbitmq** service/container can attach its stored data with the volume which may be usedfule to redundancy and safekeeping purpose in case of rabbitmq service or docker container issues.
  ::

        $ make build-volume-dev


* Steb d. Now, the main meat of all, run the ``docker-compose up`` command to start all the services mentioned in the ``docker-comose.yml`` file.

  **BUT**, you will face issues doing this, the **Reason** is while you start the services by using ``docker-compose up`` command, the services will start 
  based on the ``depends_on`` parameter of the  ``docker-compose`` file. But even then it just starts the container in that order, but does not wait for the actual service inside the conainter to
  start.

  For example, 2 services depend on rabbitmq service, but they will start running those services just after starting the rabbitmq service, what happens is rabbitmq service even 
  if has started, the actual process inside the container takes some time to setup, meanwhile the services which depend on rabbitmq start requesting/connecting to it and keeeps failing 
  and thus results in errors and container/service shutdown. 

  To prevent this, you can start the **rabbitmq** service first and then after some seconds start the full **docker-compose up** based services. You could also use something like a 
  ``wait-for-it.sh`` script which waits for few services to start and only then start itself which can be done, and I have done it whihc you can check in other projects where I have added 
  a ``wait-for-it.sh`` script, but for simplicity just start the **rabbitq** service first.

  1. Start rabbitmq service first using the same ``docker-compose.yml`` file.
     ::

          $ make start-service-rabbitmq
  
  
  2. Start all the services again using the same ``docker-compose.yml`` file.
     ::

          $ make start

     
     **NOTE :** Even if the **rabbitmq** service has already started, when ``docker-compose up`` commands notices that, it ignores starting the **rabbitmq** service again, so don't worry about it.


* Step e. Check logs if you want by some of the check-logs make commands.
   ::

      $ make check-logs-dev
      $ make-check-logs-dev-app

* Step f. You can run a single or lot of ``curl`` commands simultaneiously to hit the main API of this `dummy_orders` service which furhter talks to `fraud_police`_ and lets `alertman`_ send emails etc if required.
   ::

        # single curl command to check the service is working properly
        $ curl http://<host>:<port>/transact  -X POST -H 'Content-type: application/json' -d '{"order": {"id": 1234, "name": "avengers 4 spoilers book", "cost": 123.00, "currency": "INR"}, "paymentMethod": "amazonpay", "payment": {"card": 1234567887654321, "type": "wallet", "amount": 123.00, "currency": "INR"} }'
   
        # run multiple curl commands in background mode to send simultaneous requests to the service to check for load
        $ for i in `seq 1 100`; do
        ( curl http://<host>:<port>/transact  -X POST -H 'Content-type: application/json' -d '{"order": {"id": 1234, "name": "avengers 4 spoilers book", "cost": 123.00, "currency": "INR"}, "paymentMethod": "amazonpay", "payment": {"card": 1234567887654321, "type": "wallet", "amount": 123.00, "currency": "INR"} }' ) &
        ( curl http://<host>:<port>/transact  -X POST -H 'Content-type: application/json' -d '{"order": {"id": 5678, "name": "bahubali vs avengers saga", "cost": 13.00, "currency": "USD"}, "paymentMethod": "icicidebit", "payment": {"card": 8765432112345678, "type": "debit", "amount": 13.00, "currency": "USD"} }' ) &
        done

        # here the host and port is the configured exposed port and hostname of the service proxying to it
        # for example curl http://192.168.10.10:9001/transact or http://192.168.10.10/transact (if exposed at port 80) or via nginx or reverse proxy

   