# Order_delay_notification_system
You can run this project with the command below:
docker-compose up


- To record the delay for the orders you can use:
127.0.0.1:8000/delay_order

- To assign the order to agent you can use:
127.0.0.1:8000/assign_order_to_agent

- To recieve the delay report of vendors you can use:
127.0.0.1:8000/recieve_delay_report

I have used Celery for this project to reduce the load on the server.



To run this program you can use this command:
docker-compose run


# Prerequisites
<br>
python 3+
<br>
Celery
<br>
Django
<br>
Redis

