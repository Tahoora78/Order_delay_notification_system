from django.db import models
from django.utils import timezone


ORDER_STATES = (
    ('DELIVERED', 'DELIVERED'),
    ('PICKED', 'PICKED'),
    ('AT_VENDOR' , 'AT_VENDOR'),
    ('ASSIGNED', 'ASSIGNED')
)
        
DELAY_STATES = (
    ('NEW_ESTIMATE', 'NEW_ESTIMATE'),
    ('DELAY_QUEUE', 'DELAY_QUEUE')
)
        

class Agent(models.Model):
    name = models.CharField(max_length=50)
    busy = models.BooleanField(default=False)
    def __str__(self) -> str:
        return f"{self.name}"


class Vendor(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f"{self.name}"


class Order(models.Model):
    name = models.CharField(max_length=50)
    delivery_time = models.IntegerField()
    registered_time  = models.DateTimeField(default=timezone.now)
    """
    for the time that deleivery time has been updated and increased
    """
    updated_delivery_time = models.IntegerField(default=0)
    checked = models.BooleanField(default=False)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.name} ,{self.delivery_time}, {self.registered_time}, {self.updated_delivery_time}, {self.checked}"

class AgentOrder(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.agent}, {self.order}"


class Trip(models.Model):
    state = models.CharField(
        max_length=10,
        choices=ORDER_STATES,
        default=ORDER_STATES[3]
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    last_update_time = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.state}, {self.order}, {self.last_update_time}"



class DelayReport(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    
    state = models.CharField(
        max_length=15,
        choices=DELAY_STATES
    )

    delay_time = models.IntegerField()

    def __str__(self) -> str:
        return f"{self.order}, {self.state}, {self.delay_time}"

