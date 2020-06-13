from django.shortcuts import render
from .models import *
# Create your views here.


def store(request):
    products = Product.objects.all()
    context = {"products": products}
    return render(request, 'store/store.html', context)


def cart(request):

    # user has logged in:
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()

    # user has not logged in:
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items_quantity': 0}

    context = {"items": items, "order_of_this_transaction": order}
    print("context:")
    print(context)
    return render(request, 'store/cart.html', context)


def checkout(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()

    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items_quantity': 0}

    context = {"items": items, "order_of_this_transaction": order}
    return render(request, 'store/checkout.html', context)
