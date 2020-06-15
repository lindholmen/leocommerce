from django.shortcuts import render
from .models import *

from django.http import JsonResponse
# Create your views here.
import json


def store(request):
    # user has logged in:
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items_quantity

    # user has not logged in:
    else:
        items = []
        order = {'get_cart_total': 0,
                 'get_cart_items_quantity': 0, "shipping": False}
        cartItems = order["get_cart_items_quantity"]

    products = Product.objects.all()
    context = {"products": products, "cartItems": cartItems}
    return render(request, 'store/store.html', context)


def cart(request):

    # user has logged in:
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items_quantity

    # user has not logged in:
    else:
        items = []
        order = {'get_cart_total': 0,
                 'get_cart_items_quantity': 0, "shipping": False}
        cartItems = order["get_cart_items_quantity"]

    context = {"items": items, "order_of_this_transaction": order,
               'cartItems': cartItems}

    return render(request, 'store/cart.html', context)


def checkout(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items_quantity

    else:
        items = []
        order = {'get_cart_total': 0,
                 'get_cart_items_quantity': 0, "shipping": False}
        cartItems = order["get_cart_items_quantity"]

    context = {"items": items, "order_of_this_transaction": order,
               'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print("Action:", action)
    print("ProductId:", productId)
    print("Customer:", request.user.customer)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(
        order=order, product=product)

    if action == 'add':
        orderItem.quantity += 1
    elif action == "remove":
        orderItem.quantity -= 1

    print("quantity of the orderItem:", orderItem.quantity)
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)
