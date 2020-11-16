from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.contrib import messages

from products.models import Product
# Create your views here.

def view_cart(request):
    """ A view to show contents of the cart """
    return render(request, 'cart/view_cart.html')

def add_to_cart(request, item_id):
    product = get_object_or_404(Product, pk=item_id)
    quantity = int(request.POST.get('quantity'))
    redirect_url = request.POST.get('redirect_url')
    cart = request.session.get('cart', {})

    
    
    if item_id in list(cart.keys()):
        cart[item_id] += quantity
        messages.success(request, f'Updated {product.name} quantity to {cart[item_id]}')
    else:
        cart[item_id] = quantity
        messages.success(request, f'Added {product.name} to your cart')
    print(f'Added {product.name} to your cart')
    print(quantity)

    request.session['cart'] = cart
    print(request.session['cart'])
    return redirect(redirect_url)

def remove_from_cart(request, item_id):
    print("remove item from cart")
    product = get_object_or_404(Product, pk=item_id)
    cart = request.session.get('cart', {})
    cart.pop(item_id)
    request.session['cart'] = cart
    redirect_url = request.POST.get('redirect_url')
    return redirect(redirect_url)

def update_cart(request, item_id):
    print("updating cart")
    product = get_object_or_404(Product, pk=item_id)
    quantity = int(request.POST.get('quantity'))
    cart = request.session.get('cart', {})
    if quantity > 0:
        cart[item_id] = quantity
        messages.success(request,
                            (f'Updated {product.name} '
                            f'quantity to {cart[item_id]}'))
    else:
        cart.pop(item_id)
        messages.success(request,
                            (f'Removed {product.name} '
                            f'from your cart'))

    request.session['cart'] = cart
    return redirect(reverse('view_cart'))
