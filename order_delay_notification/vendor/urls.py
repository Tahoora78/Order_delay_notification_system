from django.urls import path
from . import views

urlpatterns = [
    path("delay_order", views.delay_order),
    path("assign_order_to_agent/<order_id>", views.assign_order_to_agent, name="order_id"),
    path("recieve_delay_report", views.recieve_vendor_delay_reports)
]