from django.contrib.auth.models import Permission, Group
from django.core.management import call_command
from core.models import Bike, BikeLocation, BikeRental, Subscription, SubscriptionType, CustomUser, PaymentInfo
from datetime import datetime, timedelta
import random
import os
import glob

def loadbasedata():
    #check if basedata is already present, otherwise add
     
    #SubscriptionTypes
    if not SubscriptionType.objects.exists():
        SubscriptionType.objects.create(title="365-day pass", description="Ride as much as you want for an entire year (365 days). Ideal for the frequent user who likes to keep it uncomplicated.", sub_price=589, sub_duration=365)
        SubscriptionType.objects.create(title="30-day subscription", description="Ride as often as you want for 30 days.", sub_price=259, sub_duration=30)
        SubscriptionType.objects.create(title="24-hour pass", description="Tourist in oslo? This pass provides 24 hours of access to our entire network of bikes!", sub_price=39, sub_duration=1)
    
    #Bikes
    if not Bike.objects.exists():
        latmin = 59.90855
        latmax = 59.92736
        longmin = 10.73551
        longmax = 10.77773
        for i in range(20):
            bike = Bike.objects.create()
            BikeLocation.objects.create(bike=bike, latitude=round(random.uniform(latmin, latmax),5), longitude=round(random.uniform(longmin, longmax),5))
    
    #Permissions
    apiuser, _ = Group.objects.get_or_create(name="User")
    fleetmanager, _ = Group.objects.get_or_create(name="Fleet Manager")
    bikegroup, _ = Group.objects.get_or_create(name="Bike")

    view_bike = Permission.objects.get(codename="view_bike")
    view_bikelocation = Permission.objects.get(codename="view_bikelocation")
    view_bikerental = Permission.objects.get(codename="view_bikerental")
    view_user = Permission.objects.get(codename="view_customuser")
    change_bike = Permission.objects.get(codename="change_bike")
    change_bikerental = Permission.objects.get(codename="change_bikerental")
    change_user = Permission.objects.get(codename="change_customuser")
    add_bike = Permission.objects.get(codename="add_bike")
    add_bikelocation = Permission.objects.get(codename="add_bikelocation")
    add_bikerental = Permission.objects.get(codename="add_bikerental")
    delete_bike = Permission.objects.get(codename="delete_bike")
    delete_bikelocation = Permission.objects.get(codename="delete_bikelocation")
    delete_bikerental = Permission.objects.get(codename="delete_bikerental")

    apiuser_permissions = [
        view_bike,
        view_bikelocation,
        view_bikerental,
        view_user,
        change_bikerental,
        change_user,
        add_bikerental
    ]
    fleetmanager_permissions = [
        view_bike,
        view_bikelocation,
        view_bikerental,
        change_bike,
        change_bikerental,
        add_bike,
        add_bikelocation,
        add_bikerental,
        delete_bike,
        delete_bikelocation,
        delete_bikerental
    ]
    bikegroup_permissions = [
        view_bike,
        change_bike,
        add_bikelocation
    ]
    apiuser.permissions.set(apiuser_permissions)
    fleetmanager.permissions.set(fleetmanager_permissions)
    bikegroup.permissions.set(bikegroup_permissions)

    #Admin user
    if not CustomUser.objects.filter(is_superuser=True).exists():
        admin, created = CustomUser.objects.get_or_create(email="admin@baas.no", defaults={'first_name': 'admin', 'last_name': 'admin'})
        admin.is_staff = True
        admin.is_superuser = True
        if created:
            admin.set_password("admin")
        admin.save()

    #User that the bikes will use to authenticate
    bikeuser, created = CustomUser.objects.get_or_create(email="bike@baas.no", defaults={'first_name': 'bike', 'last_name': 'account'})
    bikeuser.groups.add(bikegroup)
    if created:
        bikeuser.set_password("0000")
        bikeuser.save()

def populate_user(user):
    if BikeRental.objects.filter(user=user).exists():
        return
    #Add a random bike rental history to a user if the user has no previous records
    #Choose a start date from 30-180 days ago
    start_date = datetime.today() - timedelta(days=random.randint(30, 100))
    #Create a fake credit card
    expiration_year = start_date.year + random.randint(0,4)
    card = PaymentInfo.objects.create(user=user, title="visa", card_number=f'402960{random.randint(1111111111, 9999999999)}', cvv=random.randint(111,999), expiration_year=expiration_year, expiration_month=random.randint(1,12))

    #Create at least a 30-day subscription, or a random one if that doesnt exist
    subtype = SubscriptionType.objects.filter(sub_duration__gte=30)
    if not subtype.exists():
        subtype = SubscriptionType.objects.all()
    Subscription.objects.get_or_create(user=user, defaults={'subscriptiontype': random.choice(subtype), 'start_time': start_date.date(), 'payment': card})

    latmin = 59.90855
    latmax = 59.92736
    longmin = 10.73551
    longmax = 10.77773
    for i in range(30):
        #Half of the time, register a bike rental, otherwise go to next day
        if random.random() > 0.5:
            start_time = datetime(start_date.year, start_date.month, start_date.day, random.randint(6, 23), random.randint(0, 59), random.randint(0, 59))
            end_time = start_time + timedelta(minutes=random.randint(15, 100))
            #Find a bike with no existing bikelocations during that time. If there are no bikes, create a new bike
            bike_exclude_list = BikeLocation.objects.filter(time__range=(start_time, end_time)).values_list('bike', flat=True).distinct()
            bikes = Bike.objects.exclude(pk__in=bike_exclude_list)
            count = bikes.count()
            if count > 0:
                bike = bikes[random.randint(0, count-1)]
            else:
                bike = Bike.objects.create()
            BikeLocation.objects.create(bike=bike, latitude=round(random.uniform(latmin, latmax),5), longitude=round(random.uniform(longmin, longmax),5), time=start_time)
            BikeLocation.objects.create(bike=bike, latitude=round(random.uniform(latmin, latmax),5), longitude=round(random.uniform(longmin, longmax),5), time=end_time)
            rental = BikeRental.objects.create(bike=bike, user=user, start_time=start_time, end_time=end_time)
            rental.save()
            rental.calculate_cost()
            rental.create_receipt()
        start_date = start_date + timedelta(days=1)

def reset():
    call_command("flush", verbosity=0, interactive=False)
    files = glob.glob('/files/receipts/*')
    for f in files:
        os.remove(f)
    loadbasedata()