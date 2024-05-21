from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import datetime
from .managers import CustomUserManager

STATUS_CHOICES = [
    ("A", "Available"),
    ("B", "Busy"),
    ("E", "Error"),
    ("M", "Maintenance"),
]

#Custom User class to use email as username instead of dedicated username field
class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    first_name= models.CharField(blank=False, null=False, max_length=100)
    last_name = models.CharField(blank=False, null=False, max_length=100)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class PaymentInfo(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    card_number = models.CharField(max_length=19, validators=[RegexValidator("(^4[0-9]{12}(?:[0-9]{3})?$)|(^(?:5[1-5][0-9]{2}|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)[0-9]{12}$)|(3[47][0-9]{13})|(^3(?:0[0-5]|[68][0-9])[0-9]{11}$)|(^6(?:011|5[0-9]{2})[0-9]{12}$)|(^(?:2131|1800|35\d{3})\d{11}$)", "Card number is not valid")])
    cvv = models.CharField(max_length=4, validators=[RegexValidator("(^[0-9]{3,4}$)")])
    expiration_year = models.IntegerField()
    expiration_month = models.IntegerField()

    def __str__(self):
        return f'{self.user} Payment Info'

    def fourdigits(self):
        return f'{self.title}  ****{self.card_number[-4:]}'

class SubscriptionType(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    #Cost of the subscription in kroner
    price = models.IntegerField()
    #How long the subscription is valid, in days
    duration = models.IntegerField()

    def __str__(self):
        return self.title

class Subscription(models.Model):
    subscriptiontype = models.ForeignKey(SubscriptionType, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    start_time = models.DateField(default=datetime.date.today)
    auto_renewal = models.BooleanField(default = False)
    payment = models.ForeignKey(PaymentInfo, on_delete=models.SET_NULL, blank=True, null=True)

    def valid_until(self):
        return self.start_time + datetime.timedelta(days=self.subscriptiontype.duration)

    def is_valid(self):
        return self.valid_until() >= datetime.date.today()

    def __str__(self):
        return f'{self.user} Subscription'


class Bike(models.Model):
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="A")
    keycode = models.CharField(max_length=8, default="0000")

    def __str__(self):
        return f'Bike #{self.pk}'
    
    def location(self):
        return BikeLocation.objects.filter(bike=self.pk, time__lte=timezone.now()).order_by('-time').first()
    
class BikeLocation(models.Model):
    bike = models.ForeignKey(Bike, on_delete=models.CASCADE)
    latitude = models.FloatField(default=59.90756, validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.FloatField(default=10.7599, validators=[MinValueValidator(-180), MaxValueValidator(180)])
    time = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-time']

    def __str__(self):
        return f'Bike #{self.bike.pk} at lat: {self.latitude} long: {self.longitude}'

class BikeRental(models.Model):
    bike = models.ForeignKey(Bike, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True, default=None)

    def duration(self):
        if self.end_time:
            return self.end_time - self.start_time
        else:
            return f'Ongoing'
    
    def locations(self):
        return BikeLocation.objects.filter(bike=self.bike, time__range=(self.start_time, self.end_time)).order_by('time')