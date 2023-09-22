from django.shortcuts import render

# Create your views here.
def payment_required(request):
    context = {}
    return render(request, "payment/payment-required.html", context=context)
