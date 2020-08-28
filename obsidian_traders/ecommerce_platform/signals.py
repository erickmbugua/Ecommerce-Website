from django.shortcuts import get_object_or_404
from .models import Cart,Address,User_Profile,Coupon
from django.contrib.auth.models import User
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from django.db.models.signals import post_save
from ecommerce_platform.recommender import Recommender

@receiver(post_save,sender=User)
def create_user_cart_and_address_and_update_user_profile(sender,instance,created,**kwargs):
	if created:
		Cart.objects.create(user=instance)	
		Address.objects.create(user=instance)
		User_Profile.objects.create(user=instance)

@receiver(valid_ipn_received)
def payment_notification(sender,**kwargs):
	ipn=sender
	coupon_id=ipn.custom
	gross=(ipn.mc_gross*100)
	if ipn.payment_status=='Completed':
		cart=Cart.objects.get(invoice_code=ipn.invoice)
		#adding bought products into recommendation system
		r=Recommender()
		orders=cart.order_items.filter(
					ordered=False
					)
		bought_products=[order.product for order in orders]
		r.products_bought(bought_products)
		if coupon_id!=None and coupon_id!="":#not empty
			coupon=Coupon.objects.get(id=coupon_id)
			if cart.get_total_after_discount(coupon.discount)==gross:
				orders=cart.order_items.filter(
						ordered=False
						)
				for order in orders:
					order.ordered=True
					order.order_invoice_code=ipn.invoice
					order.save()
					cart.order_items.remove(order)
					cart.save()
		else:
			print (cart.get_total())
			if cart.get_total()==gross:
				orders=cart.order_items.filter(
						ordered=False
						)
				for order in orders:
					order.ordered=True
					order.order_invoice_code=ipn.invoice
					order.save()
					cart.order_items.remove(order)
					cart.save()