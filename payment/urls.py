from django.urls import path
from .views import payment_required

app_name = "payment"

urlpatterns = [
    path("payment-required", payment_required , name="payment_required")
]