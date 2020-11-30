from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Address
from wishlist.views import update_wishlist
from .forms import DefaultAddressForm, AddressForm
# Create your views here.


@login_required
def profile(request):

    profile = get_object_or_404(UserProfile, user=request.user)
    template = 'profiles/profile.html'
    addresses = Address.objects.filter(user=request.user)
    primary_address = Address.objects.filter(
        user=request.user).filter(primary_address=True)
    form = DefaultAddressForm()
    form.fields['primary_address'].choices = [
        (address.pk, address.address_line_1) for address in addresses]

    orders = profile.orders.all()
    context = {
        'profile': profile,
        'form': form,
        'primary_address': primary_address,
        'orders': orders
    }
    update_wishlist(request.user, request.session)
    return render(request, template, context)


@login_required
def addresses(request):
    template = 'profiles/addresses.html'
    addresses = Address.objects.filter(user=request.user)
    print(addresses)
    context = {
        'addresses': addresses
    }

    return render(request, template, context)


@login_required
def add_address(request):
    address_manager = Address_Manager(request)
    if request.method == 'POST':
        updated_request = request.POST.copy()
        updated_request.update({'user': request.user})
        form = AddressForm(updated_request)
        if form.is_valid():
            if form.cleaned_data['primary_address'] is True:
                address_manager.clear_previous_primary_address(request.user)
            form.save()
            return redirect(reverse('addresses'))
        else:
            print(form.errors)
    else:
        form = AddressForm()

    template = 'profiles/add_address.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


@login_required
def edit_address(request, item_id):
    address_manager = Address_Manager(request)
    address = get_object_or_404(Address, pk=item_id)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        print(form)
        if form.is_valid():
            if form.cleaned_data['primary_address'] is True:
                address_manager.clear_previous_primary_address(request.user)
            form.save()
            return redirect(reverse('addresses'))
    else:
        form = AddressForm(instance=address)

    template = 'profiles/edit_address.html'
    context = {
        'form': form,
        'address': address,
    }

    return render(request, template, context)


@login_required
def delete_address(request, item_id):
    address = get_object_or_404(Address, pk=item_id)
    address.delete()
    return redirect(reverse('addresses'))




class Address_Manager:

    def __init__(self, request):
        self.request = request

    def clear_previous_primary_address(self, user):
        print("Clearing previous primary addess")
        previous_primary_address = (
            Address.objects.filter(primary_address=True).first())
        if(previous_primary_address):
            previous_primary_address.primary_address = False
            previous_primary_address.save()
