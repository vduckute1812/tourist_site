import json
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from apps.core.utils import get_public_url
from apps.cart.cart import Cart
from apps.order.utils import checkout
from apps.order.models import Order, OrderItem
from apps.coupon.models import Coupon
from .models import Product


def api_add_to_cart(request):
    data = json.loads(request.body)
    json_response = {'success': True}
    product_id = data['product_id']
    update = data['update']
    quantity = data['quantity']
    product = get_object_or_404(Product, pk=product_id)

    cart = Cart(request)

    if not update:
        cart.add(product=product, quantity=1, update_quantity=False)
    else:
        cart.add(product=product, quantity=quantity, update_quantity=True)

    return JsonResponse(json_response)


def remove_from_cart(request):
    data = json.loads(request.body)
    json_response = {'success': True}
    product_id = str(data['product_id'])

    cart = Cart(request)
    cart.remove(product_id)

    return JsonResponse(json_response)


def create_checkout_session(request):
    # Coupon
    data = json.loads(request.body)
    coupon_code = data['coupon_code']
    coupon_value = 0

    if coupon_code != '':
        coupon = Coupon.objects.get(code=coupon_code)
        if coupon.can_use():
            coupon_value = coupon.value
            coupon.use()

    cart = Cart(request)
    stripe.api_key = settings.STRIPE_API_KEY_HIDDEN
    items = []
    for item in cart:
        product = item['product']
        price = int(product.price * 100)
        if coupon_value > 0:
            price = int(price * (int(coupon_value) / 100))

        _obj = {
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': product.title
                },
                'unit_amount': price
            },
            'quantity': item['quantity']
        }
        items.append(_obj)

    public_url = get_public_url()
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=items,
        mode='payment',
        success_url="{}/cart/success".format(public_url),
        cancel_url="{}/cart/".format(public_url),
    )

    data = json.loads(request.body)
    first_name = data['first_name']
    last_name = data['last_name']
    email = data['email']
    address = data['address']
    zipcode = data['zipcode']
    place = data['place']
    payment_intent = session.payment_intent

    order_id = checkout(request, first_name, last_name, email, address, zipcode, place)
    # total_price = 0.0
    # for item in cart:
    #     product = item['product']
    #     total_price = total_price + float(product.price) * int(item['quantity'])

    total_price = cart.get_total_cost()
    if coupon_value > 0:
        total_price = total_price * coupon_value / 100

    order = Order.objects.get(pk=order_id)
    order.paid_amount = total_price
    order.payment_intent = payment_intent
    order.used_coupon = coupon_code
    order.save()

    return JsonResponse({'session': session})


def api_checkout(request):
    cart = Cart(request)
    data = json.loads(request.body)
    json_response = {'success': True}
    first_name = data['first_name']
    last_name = data['last_name']
    email = data['email']
    address = data['address']
    zipcode = data['zipcode']
    place = data['place']

    # TODO: CREATE ORDER
    order_id = checkout(request, first_name, last_name, email, address, zipcode, place)
    paid = True

    if paid == True:
        order = Order.objects.get(pk=order_id)
        order.paid = True
        order.paid_amount = cart.get_total_cost()
        order.save()
        cart.clear()
    return redirect('/')
