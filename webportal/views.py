from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.utils import dateparse
from django.db.models import Q
import datetime
from core.models import PaymentInfo, BikeRental, SubscriptionType, CustomUser, Bike, BikeLocation
from core.forms import CustomUserCreationForm, CustomUserChangeForm, SubscriptionUpdateForm, PaymentInfoCreationForm

#frontpage
def home(request):
    context = {
        'subscriptions': SubscriptionType.objects.all(),
        'bikecount': Bike.objects.all().count(),
    }
    return render(request, "webportal/home.html", context)

#Show current location of all bikes
def bikemap(request):
    context = {
        'bikes': Bike.objects.filter(status="A")
    }
    return render(request, "webportal/bikemap.html", context)

#Create a new account
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            group = Group.objects.get(name="User")
            user.groups.add(group)
            messages.success(request, f'Account has been created! You are now able to log in')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, "webportal/register.html", {'form': form})

@login_required
def profile(request, pk):
    user = CustomUser.objects.filter(pk=pk).first()
    if request.method == 'POST':
        u_form = CustomUserChangeForm(request.POST, instance=user)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, f'Profile has been updated!')
            return redirect('webportal-profile', pk=user.pk)
    else:
        u_form = CustomUserChangeForm(instance=user)
    
    rentals = BikeRental.objects.filter(user=user).order_by('-start_time')
    if request.GET.get('search'):
        try:
            date = dateparse.parse_datetime(request.GET.get('search'))
        except ValueError:
            pass
        else:    
            rentals = rentals.filter(start_time__gte=datetime.datetime(date.year, date.month, date.day, 0, 0, 0), start_time__lte=datetime.datetime(date.year, date.month, date.day, 23, 59, 59))

    context = {
        'user': user,
        'u_form': u_form,
        'rentals': rentals,
    }
    return render(request, "webportal/profile.html", context)

@login_required
def bikeRentalDetail(request, pk):
    bikerental = get_object_or_404(BikeRental, pk=pk, user=request.user)
    context = {
        'bikerental': bikerental,
        'locations': bikerental.locations()
    }
    return render(request, "webportal/bikerental.html", context)

@login_required
def updateSubscription(request):
    if request.method == 'POST' and hasattr(request.user, 'subscription'): #Change existing subscription
        form = SubscriptionUpdateForm(request.POST, instance=request.user.subscription)
        if form.is_valid():
            sub = form.save(commit=False)
            if sub.subscriptiontype == request.user.subscription.subscriptiontype and request.user.subscription.is_valid():
                #if subscription type did not change, keep the old start time
                sub.start_time = request.user.subscription.start_time
            else:
                sub.start_time = datetime.date.today()
            sub.user = request.user
            sub.save()
            messages.success(request, "Subscription was updated!")
            return redirect("webportal-profile", pk=request.user.pk)
    elif request.method == 'POST': #Create new subscription
        form = SubscriptionUpdateForm(request.POST)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.start_time = datetime.date.today()
            sub.user = request.user
            sub.save()
            messages.success(request, "Subscription was created!")
            return redirect("webportal-profile", pk=request.user.pk)
    elif hasattr(request.user, 'subscription'):
        form = SubscriptionUpdateForm(instance=request.user.subscription)
    else:
        form = SubscriptionUpdateForm()
    context = {
        'subscriptions': SubscriptionType.objects.all(),
        'paymentinfo': PaymentInfo.objects.filter(user=request.user),
        'form': form
    }
    return render(request, "webportal/subscription.html", context)

@login_required
def paymentInfo(request):
    if request.method == 'POST':
        form = PaymentInfoCreationForm(request.POST)
        if form.is_valid():
            p = form.save(commit=False)
            p.user = request.user
            p.save()
            messages.success(request, "Paymentinfo was added!")
            return redirect('webportal-payment')
    else:
        form = PaymentInfoCreationForm()
    context = {
        'paymentinfo': PaymentInfo.objects.filter(user=request.user),
        'form': form
    }
    return render(request, "webportal/paymentinfo.html", context)

@login_required
def deletePaymentInfo(request, pk):
    paymentinfo = PaymentInfo.objects.filter(pk=pk, user=request.user).first()
    if paymentinfo:
        paymentinfo.delete()
        messages.info(request, "Paymentinfo was deleted")
    else:
        messages.error(request, "Something went wrong, please try again")
    return redirect('webportal-payment')