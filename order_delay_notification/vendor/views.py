from django.shortcuts import render
from django.http import HttpResponse
from .tasks import test_func
from queue import Queue
from django.core.cache import cache
from .models import Agent, Order, Trip, ORDER_STATES, DelayReport, DELAY_STATES
from django.db import connection
from django.db.models import Q
from datetime import timezone
import datetime
from django.db.models.functions import Extract, Now, Trunc
from tasks import *



agents_cache_key = 'available_agents'
delay_order_cache_key = 'delay_orders'
cache_time = 86400


def recieve_delayed_trip_order():
    result = []
    with connection.cursor() as cursor:
        cursor.execute("SELECT order FROM Trip where last_update_time-order.registered_time>=order.delivery_time+order.updated_delivery_time")
        result = cursor.fetchall()
    return result

def calculate_difference_in_minutes(time_):
    difference = (datetime.datetime.now().replace(tzinfo=None) - time_.replace(tzinfo=None)).total_seconds()/60
    return difference



def delay_order(request):
    """
    1) query all order that has passed their time 
        - orders that are in trip with state ["as","pi", "at"] --> 
            new time set and save in delay and report to user
            and update delivery time and set has_delay=false
        - that are not in trip table  ---> add to delay queue, has_delay (order) = true
        - are in trip table with state="delivered" --> add to delay queue has_delay=true
        save to delay_report table
    """
    estimate_new_time()
    add_to_delay_order_queue()

    return HttpResponse("Delay calculated")



def assign_order_to_agent(request, order_id):
    """
    for all orders in delay_order_queue
    1) remove one order from delay_order_queue
    2) remove one agent from available_agent_queue
    3) save order and agent in order_agent_table
    4) change the trip order status to "assigned"
    5) change the order table check to false
    """
    assign_order_to_aggent()
    return HttpResponse("Delay ordered assigned to available agents")
    

def set_available_agents(agent_queue):
    cache_time = 86400
    cache.set(agents_cache_key, agent_queue, cache_time)


def get_available_agents():
    cache_time = 86400
    data = cache.get(agents_cache_key)

    if not data:
        available_agent_queue = Queue()
        agents = Agent.objects.all()
        for agent in agents:
            available_agent_queue.put(agent.id)
        
    cache.set(agents_cache_key, available_agent_queue, cache_time)
    return cache.get(agents_cache_key)


def recieve_endor_delay_reports(request):
    result = get_delay_report()
    return HttpResponse(result)
