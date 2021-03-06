from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from profiles.forms import AddressForm
from profiles.views import Address_Manager
from .models import Order, OrderLineItem
from products.models import Product
from profiles.models import UserProfile
from django.conf import settings
import re
import json
import time


class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    def _send_confirmation_email(self, order):
        """Send the user a confirmation email"""
        cust_email = order.email
        subject = render_to_string(
            'checkout/confirmation_emails/confirmation_email_subject.txt',
            {'order': order})
        body = render_to_string(
            'checkout/confirmation_emails/confirmation_email_body.txt',
            {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL})

        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [cust_email]
        )


    def handle_event(self, event):
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200)

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe
        """
        intent = event.data.object
        pid = intent.id
        billing_details = intent.charges.data[0].billing_details
        first_name, last_name = billing_details.name.split(" ", 1)
        cart = intent.metadata.cart
        save_info = intent.metadata.save_info
        grand_total = round(intent.charges.data[0].amount / 100, 2)
        profile = None
        username = intent.metadata.username
        
        if username != 'AnonymousUser':
            profile = UserProfile.objects.get(user__username=username)
            if save_info:
                address_data = {'user': profile.user,
                                'first_name': first_name,
                                'last_name': last_name,
                                'address_line_1': billing_details.address.line1,
                                'address_line_2': billing_details.address.line2,
                                'town_or_city': billing_details.address.city,
                                'county_or_province': billing_details.address.state,
                                'country': billing_details.address.country,
                                'post_code_or_zip_code':
                                billing_details.address.postal_code,
                                'phone_number': billing_details.phone,
                                'primary_address': True}
   
                address_form = AddressForm(address_data)
                address_manager = Address_Manager()
                if address_manager.address_already_exists(address_form) is False:
                    address_manager.clear_previous_primary_address(profile.user)
                    new_primary_address = address_form.save()
                    profile.primary_address = new_primary_address
                    profile.save()
        
        order_exists = False
        attempt = 1
        while attempt <= 5:
            try:
                order = Order.objects.get(stripe_pid=pid)
                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)

        if order_exists:
            self._send_confirmation_email(order)
            return HttpResponse(content=(f'Webhook received: {event["type"]} | SUCCESS: ' 'Verified order already in database'), status=200)
        else:
            order = None
            try:
                order = Order.objects.create(
                    user_profile=profile,
                    email=billing_details.email,
                    first_name=first_name,
                    last_name=last_name,
                    address_line_1=billing_details.address.line1,
                    address_line_2=billing_details.address.line2,
                    town_or_city=billing_details.address.city,
                    county_or_province=billing_details.address.state,
                    country=billing_details.address.country,
                    post_code_or_zip_code=billing_details.address.postal_code,
                    phone_number=billing_details.phone,
                    stripe_pid=pid,
                )
                for item_id, item_data in json.loads(cart).items():
                    product = Product.objects.get(id=item_id)
                    order_line_item = OrderLineItem(
                        order=order,
                        product=product,
                        quantity=item_data,)
                    order_line_item.save()
            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(content=f'Webhook received: {event["type"]} | ERROR: {e}', status=500)
        self._send_confirmation_email(order)
        return HttpResponse(content=(f'Webhook received: {event["type"]} | SUCCESS: ''Created order in webhook'), status=200)

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """

        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)
