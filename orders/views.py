from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from .models import OrderItem, Order
from .forms import RUOrderCreateForm, USOrderCreateForm
from cart.cart import Cart
from .tasks import order_created
from django.urls import reverse
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
import weasyprint

@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    html = render_to_string('orders/order/pdf.html', {'order': order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="order_{order_id}.pdf"'
    weasyprint.HTML(string=html).write_pdf(response, stylesheets=[weasyprint.CSS(settings.STATIC_ROOT / 'css/pdf.css')])
    return response
def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        if request.LANGUAGE_CODE == 'ru':
            form = RUOrderCreateForm(request.POST)
        else:
            form = USOrderCreateForm(request.POST)

        if form.is_valid():
            order = form.save(commit=False)
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount
            order.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
            #очистить корзину
            cart.clear()
            #запустить асинхронное задание
            order_created.delay(order.id)
            #задать заказ в сеансе
            request.session['order_id'] = order.id
            #перенаправить к платежу
            return redirect(reverse('payment:process'))
    else:
        if request.LANGUAGE_CODE == 'ru':
            form = RUOrderCreateForm(request.POST)
        else:
            form = USOrderCreateForm(request.POST)
    return render(request,
                  'orders/order/create.html',
                  {'form': form, 'cart': cart})

@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request,
                  'admin/orders/order/detail.html',
                  {'order': order})