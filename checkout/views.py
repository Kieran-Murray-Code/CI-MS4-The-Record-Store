from django.shortcuts import (
    render, redirect, reverse, get_object_or_404, HttpResponse
)
from .forms import OrderForm
from profiles.models import UserProfile
from products.models import Product
from .models import Order, OrderLineItem
from django.conf import settings
from cart.contexts import cart_contents
import stripe
# import json
# Create your views here.


def checkout(request):

    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    if request.method == 'POST':
        print("Checkout POST")
        cart = cart_contents(request)
        user = request.user
        original_request = request.POST.copy()
        updated_request = add_hidden_info(original_request, cart, user)
        order_form = OrderForm(updated_request)

        if order_form.is_valid():
            print("Checkout Order Form Is Valid")
            order = order_form.save(commit=False)
            order.save()

            for cart_item in cart['cart_items']:
                product = Product.objects.get(id=cart_item['item_id'])
                order_line_item = OrderLineItem(
                    order=order,
                    product=product,
                    quantity=cart_item['quantity'],
                )
                order_line_item.save()

            return redirect(reverse('checkout_success', args=[order.order_number]))

        else:
            print(order_form.errors)
    else:
        if request.user.is_authenticated:
            user_profile = UserProfile.objects.get(user=request.user)
            user_primary_address = user_profile.primary_address
            order_form = OrderForm(instance=user_primary_address)
            order_form.fields["email"].initial = user_profile.user.email
        else:
            order_form = OrderForm()

        current_cart = cart_contents(request)
        total = current_cart['total']
        stripe_total = round(total * 100)
        stripe.api_key = stripe_secret_key
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
            metadata={'integration_check': 'accept_a_payment'},
        )

    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }

    return render(request, template, context)


def checkout_success(request, order_number):
    template = 'checkout/checkout_success.html'
    context = {}

    return render(request, template, context)


def add_hidden_info(original_request, cart, user):
    original_request.update(
        {'user_profile': UserProfile.objects.get(user=user)})
    original_request.update(
        {'delivery_cost': cart['delivery_cost']})
    original_request.update(
        {'order_total': cart['total']})
    original_request.update(
        {'grand_total': cart['grand_total']})
    return original_request
