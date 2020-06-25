import json
from .models import *


def cookie_cart(request):
    try:
        cart = json.loads(request.COOKIES["cart"])
    except:
        cart = {}

    print(cart)
    items = []

    order = {'get_cart_total': 0,
             'get_cart_items_quantity': 0, "shipping": False}
    cartItems = order["get_cart_items_quantity"]

    for k, v in cart.items():
        try:
            cartItems += v["quantity"]

            product = Product.objects.get(id=k)
            total = product.price * v["quantity"]

            order["get_cart_total"] += total
            order["get_cart_items_quantity"] += v["quantity"]

            item = {
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'imageURL': product.imageURL
                },
                'quantity': v['quantity'],
                'get_total': total
            }
            items.append(item)

            if product.digital == False:
                order['shipping'] = True

        except:
            pass

    if order['get_cart_total'] >= 500:
        order['get_cart_total_including_shipping'] = order['get_cart_total']
    elif order['shipping']:
        order['get_cart_total_including_shipping'] = order['get_cart_total'] + 60
    else:
        order['get_cart_total_including_shipping'] = order['get_cart_total']

    return {"cartItems": cartItems, "order": order, "items": items}


def cart_data(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items_quantity

    else:
        cookieData = cookie_cart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']

    return {"cartItems": cartItems, "order": order, "items": items}


def guest_order(request, data):
    print("user not logged in")

    name = data['form']['name']
    email = data['form']['email']

    cookie_data = cookie_cart(request)
    items = cookie_data['items']
    customer, created = Customer.objects.get_or_create(
        email=email)
    customer.name = name
    customer.save()

    order = Order.objects.create(customer=customer, complete=False)
    for item in items:
        product = Product.objects.get(id=item['product']['id'])

        orderItem = OrderItem.objects.create(
            product=product,
            order=order,
            quantity=item['quantity']
        )
    return customer, order
