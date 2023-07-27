from __future__ import absolute_import, unicode_literals
import datetime
from celery import shared_task
from django.core.cache import cache
# from .views import delay_order_cache_key, agents_cache_key,cache_time
from .models import *
import requests
from django.db.models import Q
from queue import Queue
from datetime import timedelta
from django.db.models import Sum
import os

# os.environ[ 'DJANGO_SETTINGS_MODULE' ] = "order_delay_notification.settings"
agents_cache_key = 'available_agents'
delay_order_cache_key = 'delay_orders'
cache_time = 86400

def calculate_difference_in_minutes(time_):
    difference = (datetime.datetime.now().replace(tzinfo=None) - time_.replace(tzinfo=None)).total_seconds()/60
    return difference


def get_estimated_time():
    response = requests.get('https://run.mocky.io/v3/122c2796-5df4-461c-ab75-87c1192b17f7')
    data = response.json()
    return data['data']['eta']
    

@shared_task
def estimate_new_time():
    trips = Trip.objects.filter(state__in=list(map(lambda x: x[0], ORDER_STATES[1:4])))
    for trip in trips:   
        if not(trip.order.checked):  
            if calculate_difference_in_minutes(trip.order.registered_time)>trip.order.delivery_time:
                trip.order.updated_delivery_time = trip.order.updated_delivery_time + get_estimated_time()
                trip.order.checked = True
                trip.order.save()

                delay_time = calculate_difference_in_minutes(trip.order.registered_time)-trip.order.delivery_time+get_estimated_time()
                delay_report = DelayReport(
                    order=trip.order, 
                    state=DELAY_STATES[0],
                    delay_time = delay_time
                )
                delay_report.save()



def add_to_agent_cache_queue(parameter):
    agent_queue = cache.get(agents_cache_key)
    agent_queue.put(parameter)
    cache.set(agents_cache_key, agent_queue, cache_time)


def get_agent_cache_queue():
    if cache.get(agents_cache_key).empty():
        available_agent_queue = Queue()
        agents = Agent.objects.filter(busy=False)
        if (len(agents)==0):
            return 0
        for agent in agents:
            available_agent_queue.put(agent)
        cache.set(agents_cache_key, available_agent_queue, cache_time)

    agent_queue = cache.get(agents_cache_key)
    parameter = agent_queue.get()
    cache.set(agents_cache_key, agent_queue, cache_time)
    return parameter


def add_to_delay_order_cache_queue(parameter):
    delay_order_queue = cache.get(delay_order_cache_key)
    delay_order_queue.put(parameter)
    cache.set(delay_order_cache_key, delay_order_queue, cache_time)


def remove_delay_order_cache_queue():
    if (cache.get(delay_order_cache_key).empty()):
        return 0
    delay_order_queue = cache.get(delay_order_cache_key)
    parameter = delay_order_queue.get()
    cache.set(delay_order_cache_key, delay_order_queue, cache_time)
    return parameter


@shared_task
def add_to_delay_order_queue():
    delivered_trip = Trip.objects.filter(state = ORDER_STATES[0])
    for trip in delivered_trip:
        if not(trip.order.checked) and calculate_difference_in_minutes(trip.order.registered_time)>trip.order.delivery_time:
            trip.order.check = True
            trip.order.save()
            
            add_to_delay_order_cache_queue(trip.order)

            delay_time = (trip.last_update_time.replace(tzinfo=None) - trip.order.registered_time.replace(tzinfo=None))/60 - trip.order.delivery_time
            delay_report = DelayReport(order=trip.order, state=DELAY_STATES[1][0], delay_time=delay_time)
            delay_report.save()
            

    orders_without_trip = Order.objects.exclude(Q(trip__isnull=False) | Q(checked=True))    
    for order in orders_without_trip:
        if calculate_difference_in_minutes(order.registered_time)>order.delivery_time:
            order.check = True
            order.save()

            add_to_delay_order_cache_queue(order)
            delay_report = DelayReport(order=order, state=DELAY_STATES[1][0], delay_time=0)
            delay_report.save()


@shared_task
def assign_order_to_aggent():    
    delay_order = remove_delay_order_cache_queue()
    agent = get_agent_cache_queue()
    
    while(delay_order != 0 and agent != 0):
        delay_order.state = ORDER_STATES[3]
        delay_order.save()

        agent.busy = True
        agent.save()

        agent_order = AgentOrder(agent=agent, order=delay_order)
        agent_order.save()
        
        delay_order = remove_delay_order_cache_queue()
        agent = get_agent_cache_queue()


@shared_task
def get_delay_report():
    result = DelayReport.objects.values('order__vendor__name', 'delay_time').annotate(total_delay_time=Sum('delay_time')).order_by('delay_time')
    return result







