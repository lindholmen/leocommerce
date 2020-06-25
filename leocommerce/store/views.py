from django.shortcuts import render
from .models import *
from .utils import cookie_cart, cart_data, guest_order

from django.http import JsonResponse
# Create your views here.
import json
import datetime
import uuid


def store(request):
    data = cart_data(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    products = Product.objects.all()
    context = {"products": products, "cartItems": cartItems}
    return render(request, 'store/store.html', context)


def cart(request):

    data = cart_data(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {"items": items, "order_of_this_transaction": order,
               'cartItems': cartItems}

    return render(request, 'store/cart.html', context)


def checkout(request):

    data = cart_data(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

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


def processOrder(request):
    #transaction_id = datetime.datetime.now().timestamp()
    transaction_id = uuid.uuid1()
    data = json.loads(request.body)
    print(data["form"])
    print(data["shipping"])

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)

    else:
        customer, order = guest_order(request, data)

    total = float(data["form"]["totalAmount"])
    order.transaction_id = transaction_id
    print("transaction id:", transaction_id)

    if order.shipping == True:
        # which means it requires shipping
        if total == float("{:.2f}".format(order.get_cart_total_including_shipping)):
            order.complete = True
            print("require shipping, complete set to true")
    else:
        # which means it does not require shipping
        if total == float("{:.2f}".format(order.get_cart_total)):
            order.complete = True
            print("not require shipping, complete set to true")

    order.save()

    if order.shipping == True:
        print("started to create shipping address")
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode']
        )

    return JsonResponse("Payment complete!", safe=False)
