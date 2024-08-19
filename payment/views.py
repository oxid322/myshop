from django.shortcuts import render, redirect, reverse, get_object_or_404
from decimal import Decimal
import stripe
from django.conf import settings
from orders.models import Order
import uuid
from yookassa import Configuration, Payment

#создать экземпляр Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


def payment_process(request):
    summ = 0
    order_id = request.session.get('order_id', None)
    order = get_object_or_404(Order, pk=order_id)
    if request.method == 'POST':
        success_url = request.build_absolute_uri(reverse('payment:completed'))
        cancel_url = request.build_absolute_uri(reverse('payment:canceled'))
        #данные сеанса оформления платежа Stripe
        session_data = {
            'mode': 'payment',
            'client_reference_id': order.id,
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': []
        }
        #добавить товарные позиции заказа в сеанс оформления платежа Stripe
        for item in order.items.all():
            summ += item.price
            session_data['line_items'].append({
                 'price_data': {
                     'unit_amount': int(item.price * Decimal('100')),
                     'currency': 'usd',
                     'product_data': {
                         'name': item.product.name,
                     },
                 },
                 'quantity': item.quantity,
            })
        #Создать платеж Юкассы
        # Configuration.account_id = settings.UKASSA_SHOPID
        # Configuration.secret_key = settings.UKASSA_SECRET_KEY
        # payment1 = Payment.create({
        #     'amount': {
        #         'value': summ,
        #         'currency': 'RUB',
        #     },
        #     'capture': True,
        #     'confirmation': {
        #         'type':  'redirect',
        #         'return_url': success_url,
        #     },
        #     'description': 'lol'
        # }, uuid.uuid4())
        if order.coupon:
            stripe_coupon = stripe.Coupon.create(name=order.coupon.code,
                                                 percent_off=order.discount,
                                                 duration='once')
            session_data['discounts'] = [{
                'coupon': stripe_coupon.id
            }]
        #создать сеанс оформления платежа Stripe
        session = stripe.checkout.Session.create(**session_data)

        #перенаправить к платежной форме Юкассы
        return redirect(session.url, code=303)
    else:
        return render(request, 'payment/process.html', locals())


def payment_completed(request):
    return render(request, 'payment/completed.html')


def payment_canceled(request):
    return render(request, 'payment/canceled.html')
