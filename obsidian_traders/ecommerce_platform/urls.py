from django.urls import path
from . import views

app_name='ecommerce_platform'

urlpatterns=[
	path("",views.home,name="home"),
	path("my-cart/",views.my_cart,name="cart"),
	path("pending-orders/",views.pending_orders,name="pending_orders"),
	path("signup/", views.signup, name='signup'),
	path("accounts/",views.my_account,name='accounts'),
	path("check-out/",views.check_out,name="check_out"),
	path("paypal-payment/",views.paypal,name="paypal"),
	path("paypal-payment-done/",views.paypal_payment_done,name="paypal_payment_done"),
	path("paypal-payment-cancelled/",views.paypal_payment_cancelled,name="paypal_payment_cancelled"),
	path("stripe-payment/",views.stripe,name="stripe"),
	path("apply-coupon/",views.apply_coupon,name="apply_coupon"),
	path("personal-info-change/",views.account_details_change,name="account_details_change"),
	path("address-change/",views.address_change,name="address_change"),
	path("product/<slug>/",views.product_detail,name="product_detail"),
	path("<category>/",views.product_category,name="product_category"),
	path("add-to-cart/<slug>/",views.add_to_cart,name="add_to_cart"),
	path("remove-from-cart/<slug>/",views.remove_from_cart,name="remove_from_cart"),	
	path("update-cart-quantity/<slug>/",views.update_cart_quantity,name="update_cart_quantity"),
	#path("payment/",views.payment,name="payment"),
	#path("payment_successful/",views.payment_successful,name="payment_successful"),
	]