from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.scripts import populate_user, reset


@login_required
def populate_profile(request):
    populate_user(request.user)
    messages.success(request, f'Profile data added!')
    return redirect('webportal-profile', pk=request.user.pk)

@login_required
def full_reset(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        if password == "iamsure":
            reset()
    return render(request, "core/reset.html")