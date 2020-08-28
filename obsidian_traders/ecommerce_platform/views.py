from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView,ListView,View
from django.contrib.auth import login, authenticate
from django.http import HttpResponseRedirect,HttpResponse,JsonResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from ecommerce_platform.models import Product,OrderItem,Cart,Address,User_Profile,Coupon,Comment,Category
from .forms import SignUpForm,UpdateQuantityForm,CheckOutForm,CouponForm,CommentForm, AccountDetailsChangeForm,AddressChangeForm
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import string
import random
from datetime import datetime, timedelta 
from .recommender import Recommender

def create_ref_code():
	return ''.join(random.choices(string.ascii_lowercase+string.digits,k=10))

def home(request):
	categories=Category.objects.all()
	products=Product.objects.all()
	context={
		"products":products,
		"categories":categories,
	}
	return render(request,"home.html",context)
def product_detail(request,slug):
	product=Product.objects.get(slug=slug)
	comments=Comment.objects.filter(product=product)
	if request.method=="POST":
		form=CommentForm(request.POST)
		if form.is_valid():
			comment=Comment(
				author=form.cleaned_data["author"],
				body=form.cleaned_data["body"],
				product=product
				)
			comment.save()
			#buyers can only comment once
			order=OrderItem.objects.get(user=request.user,product=product,ordered=True,commented=False)
			order.commented=True
			order.save()
			messages.info(request,"Comment Sent")
			return HttpResponseRedirect(reverse('ecommerce_platform:product_detail',args=(product.slug,)))
	form=CommentForm()
	r=Recommender()
	recommended_products=r.suggest_products_for([product],4)
	#comment form only available to authenticated users
	if request.user.is_authenticated:
		#only buyers can comment
		order=OrderItem.objects.filter(user=request.user,ordered=True,commented=False,product=product)
		context={
			"product":product,
			"comments":comments,
			"form":CommentForm,
			"order":order,
			"recommended_products":recommended_products
		}
	else:
		context={
			"product":product,
			"comments":comments,
			"recommended_products":recommended_products
		}
	return render(request,"product_detail.html",context)
def product_category(request,category):
	products=Product.objects.filter(categories__name=category).order_by("-added_on")
	categories=Category.objects.all()
	context={
		"products":products,
		"categories":categories,
		"category":category
	}
	return render(request,"product_category.html",context)

def signup(request):
	if request.method=="POST":
		form=SignUpForm(request.POST)
		if form.is_valid():
			user=form.save()
			user.refresh_from_db()
			user.address.street_address=form.cleaned_data.get("street_address")
			user.address.postal_code=form.cleaned_data.get("postal_code")
			user.address.city=form.cleaned_data.get("city")
			user.address.country=form.cleaned_data.get("country")
			user.address.save()
			#user.user_profile.add(user.address)
			user.user_profile.gender=form.cleaned_data.get("gender")
			user.user_profile.phone_number=form.cleaned_data.get("phone_number")
			user.user_profile.save()
			username=form.cleaned_data.get("username")
			raw_password=form.cleaned_data.get("password1")
			user=authenticate(username=username,password=raw_password)
			login(request,user)
			return redirect("ecommerce_platform:home")
	else:
		form=SignUpForm()
	return render(request,"signup.html",{"form":form})

@login_required()
def add_to_cart(request,slug):
	product=get_object_or_404(Product,slug=slug)
	order_item,created=OrderItem.objects.get_or_create(
		user=request.user,
		product=product,
		ordered=False
		)
	cart=Cart.objects.get(user=request.user)
	if cart.order_items.filter(product__slug=product.slug).exists():
		order_item.quantity+=1
		order_item.order_item_total=order_item.get_total()
		order_item.save()
		cart.cart_total=cart.get_total()
		cart.save()
		messages.info(request,"Product quantity updated")
		return HttpResponseRedirect(reverse('ecommerce_platform:product_detail',args=(slug,)))
	else:
		cart.order_items.add(order_item)
		order_item.ordered_date=timezone.now()
		order_item.order_item_total=order_item.get_total()
		order_item.save()
		cart.cart_total=cart.get_total()
		cart.save()
		messages.info(request,"Product added to cart")
		return HttpResponseRedirect(reverse('ecommerce_platform:product_detail',args=(slug,)))

	
@login_required()
@require_POST
def update_cart_quantity(request,slug):
	product=get_object_or_404(Product,slug=slug)
	cart=Cart.objects.get(user=request.user)
	form=UpdateQuantityForm(request.POST)
	if form.is_valid():
		if cart.order_items.filter(product__slug=product.slug).exists():
			order_item=OrderItem.objects.get(
				user=request.user,
				product=product,
				ordered=False)
			order_item.quantity=form.cleaned_data["quantity"]
			order_item.order_item_total=order_item.get_total()
			order_item.save()
			cart.cart_total=cart.get_total()
			cart.save()
			return HttpResponseRedirect(reverse('ecommerce_platform:cart'))
		else:
			order_item=OrderItem.objects.create(
				user=request.user,
				product=product,
				ordered=False,
				quantity=form.cleaned_data["quantity"]
			)
			cart.order_items.add(order_item)
			order_item.ordered_date=timezone.now()
			order_item.save()
			return HttpResponseRedirect(reverse('ecommerce_platform:cart'))

@login_required()
def remove_from_cart(request,slug):
	product=get_object_or_404(Product,slug=slug)
	order_item=OrderItem.objects.get(
		user=request.user,
		product=product,
		ordered=False
		)
	cart=Cart.objects.get(user=request.user)
	if cart.order_items.filter(product__slug=product.slug).exists():
		cart.order_items.remove(order_item)
		order_item.delete()
		cart.cart_total=cart.get_total()
		cart.save()
		return redirect("ecommerce_platform:cart")

@login_required()
def my_cart(request):
	cart=Cart.objects.get(user=request.user)
	orders=cart.order_items.filter(
		ordered=False
		)
	for order in orders:
		setattr(order,"update_quantity_form",UpdateQuantityForm(initial={'quantity':order.quantity}))
	if orders.exists():
		r=Recommender()
		cart_products=[order.product for order in orders]
		recommended_products=r.suggest_products_for(cart_products,max_results=4)
		context={
			"cart":cart,
			"orders":orders,
			"recommended_products":recommended_products
		}
	else:
		context={
			"cart":cart,
			"orders":orders
		}
	return render(request,"cart.html",context)

@login_required()		
def pending_orders(request):
	pending_orders=OrderItem.objects.filter(
		user=request.user,
		ordered=True,
		delivered=False)
	for order in pending_orders:
		delivery_date=order.ordered_date+timedelta(days=4)
		setattr(order,"delivery_date",delivery_date)
	context={
		"pending_orders":pending_orders
	}
	return render(request,"pending_orders.html",context)


@login_required()
def my_account(request):
	user_profile=User_Profile.objects.get(user=request.user)
	address=Address.objects.get(user=request.user)
	context={
		"user_profile":user_profile,
		"address":address
	}
	return render(request,"my_account.html",context)

@login_required()
def check_out(request):
	cart=Cart.objects.get(user=request.user)
	address=Address.objects.get(user=request.user)
	#checking if cart total is less than allowed coupon min amount
	if request.session.get("coupon_id"):#returns true or false
		coupon_id=request.session.get("coupon_id")
		coupon=Coupon.objects.get(id=coupon_id)
		if coupon.min_amount>cart.get_total():
			del request.session["coupon_id"]	
	if request.method=="POST":
		form=CheckOutForm(request.POST)
		if form.is_valid():
			if form.cleaned_data["delivery_method"]=="Pick Up Station":
				for order in cart.order_items.all():
					order.address=form.cleaned_data["pick_up_station"]
					order.save()
			elif form.cleaned_data["delivery_method"]=="Delivery to Home or Office":
				if form.cleaned_data["shipping_address"]=="Use Default Shipping Address":
					for order in cart.order_items.all():
						order.address=address.street_address+"-"+address.postal_code+" "+address.city+","+address.country
						order.save()
				elif form.cleaned_data["shipping_address"]=="Set New Shipping Address":
					for order in cart.order_items.all():
						order.address=form.cleaned_data["street_address"]+"-"+form.cleaned_data["postal_code"]+" "+\
						form.cleaned_data["city"]+","+form.cleaned_data["country"]
						order.save()
			payment_option=form.cleaned_data["payment_option"]
			if payment_option=="PayPal":
				for order in cart.order_items.all():
					order.payment_type=payment_option
					order.save()
				return redirect("ecommerce_platform:paypal")
			elif payment_option=="Stripe":
				for order in order_items.all():
					order.payment_type=payment_option
					order.save()
				return redirect("ecommerce_platform:stripe")
		return HttpResponse("ecommerce_platform:check_out")
	coupon_form=CouponForm()
	check_out_form=CheckOutForm()
	cart=Cart.objects.get(user=request.user)
	orders=cart.order_items.filter(
		ordered=False
		)
	coupon_id=request.session.get("coupon_id")
	if coupon_id:
		coupon=Coupon.objects.get(id=coupon_id)
		cart_discounted_total=cart.get_total_after_discount(coupon.discount)
		context={
			"cart":cart,
			"address":address,
			"check_out_form":check_out_form,
			"coupon_form":coupon_form,
			"orders":orders,
			"coupon":coupon,
			"coupon_id":coupon_id,
			"cart_discounted_total":cart_discounted_total
		}
	else:
		context={
			"cart":cart,
			"address":address,
			"check_out_form":check_out_form,
			"coupon_form":coupon_form,
			"orders":orders,
			"coupon_id":coupon_id
		}
	return render(request,"check_out.html",context)


@login_required()
@require_POST
def apply_coupon(request):
	now=timezone.now()
	form=CouponForm(request.POST)
	cart=Cart.objects.get(user=request.user)
	if form.is_valid():
		try:
			coupon=Coupon.objects.get(code=form.cleaned_data["code"],
									valid_from__lte=now,
									valid_to__gte=now
									)
			id_temp=request.session.get("coupon_id")
			if id_temp!=None and id_temp!="": 
				if id_temp==coupon.id:
					messages.info(request,"You've already used this coupon")
			else:
				if cart.get_total()>=coupon.min_amount:
					request.session["coupon_id"]=coupon.id
					messages.info(request,"Coupon has been applied")
				else:
					messages.info(request,"Minimum allowable amount for this coupon is: {}".format(coupon.min_amount))
		except Coupon.DoesNotExist:
			request.session["coupon_id"]=None
			messages.info(request,"Coupon does not exist or has expired")
	return redirect('ecommerce_platform:check_out')
"""

def apply_coupon(request):
	if request.method=="POST":
		code=request.POST.get("code")
		now=timezone.now()
		cart=Cart.objects.get(user=request.user)
		data={}
		try:
			coupon=Coupon.objects.get(code=code,
									valid_from__lte=now,
									valid_to__gte=now
									)
			id_temp=request.session.get("coupon_id")
			if id_temp!=None and id_temp!="": 
				if id_temp==coupon.id:
					data["error_message"]="You've already used this coupon"
			else:
				if cart.get_total()>=coupon.min_amount:
					request.session["coupon_id"]=coupon.id
					data["is_valid"]=True
					data["success_message"]="Coupon has been applied"
				else:
					data["error_message"]="Minimum allowable amount for this coupon is: {}".format(coupon.min_amount)
		except Coupon.DoesNotExist:
			request.session["coupon_id"]=None
			data["error_message"]="Coupon does not exist or has expired"
		return JsonResponse(data)
	else:
		return JsonResponse({"na":"nope"})
"""
@login_required
def paypal(request):
	cart=Cart.objects.get(user=request.user)
	cart.invoice_code=create_ref_code()
	cart.save()
	orders=cart.order_items.filter(
		ordered=False
		)
	order_names='Orders: '
	host=request.get_host()
	for order in orders:
		order_names+str(order.order_number)+","
	coupon_id=request.session.get("coupon_id")
	if coupon_id:
		coupon=Coupon.objects.get(id=coupon_id)
		amount=cart.get_total_after_discount(coupon.discount)
	else:
		amount=cart.get_total()
	amount=amount/100
	paypal_dict={
		'business':settings.PAYPAL_RECEIVER_EMAIL,
		'amount':amount,
		'item_name': order_names,
		'invoice':cart.invoice_code,
		'custom':coupon_id,
		'currency_code':'USD',
		'notify_url':'http://{}{}'.format(host,reverse('paypal-ipn')),
		'return_url':'http://{}{}'.format(host,reverse('ecommerce_platform:paypal_payment_done')),
		'cancel_return':'http://{}{}'.format(host,reverse('ecommerce_platform:paypal_payment_cancelled')),
	}
	form=PayPalPaymentsForm(initial=paypal_dict)
	context={
		'form':form,
	}
	return render(request,'paypal.html',context)

@csrf_exempt
def paypal_payment_done(request):
	return render(request,"paypal_payment_done.html")
@csrf_exempt
def paypal_payment_cancelled(request):
	return render(request,'paypal_payment_cancelled.html')


@login_required()
def stripe(request):
	pass

@login_required()
def account_details_change(request):
	if request.method=="POST":
		form=AccountDetailsChangeForm(request.POST)
		if form.is_valid():
			user=request.user
			user.refresh_from_db()
			user.first_name=form.cleaned_data.get("first_name")
			user.last_name=form.cleaned_data.get("last_name")
			user.email=form.cleaned_data.get("email")
			user.user_profile.phone_number=form.cleaned_data.get("phone_number")
			user.user_profile.save()
			user.save()
			messages.info(request,"Personal details changed successfully")
			return redirect("ecommerce_platform:accounts")
		return redirect("ecommerce_platform:accounts")
	details_dict={
			"first_name": request.user.first_name,
			"last_name": request.user.last_name,
			"phone_number": request.user.user_profile.phone_number,
			"email": request.user.email,
	}
	form=AccountDetailsChangeForm(initial=details_dict)
	context={
		"form":form,
	}
	return render(request,"account_details_change.html",context)
			
@login_required()
def address_change(request):
	if request.method=="POST":
		form=AddressChangeForm(request.POST)
		if form.is_valid():
			user=request.user
			user.refresh_from_db()
			user.address.street_address=form.cleaned_data.get("street_address")
			user.address.postal_code=form.cleaned_data.get("postal_code")
			user.address.city=form.cleaned_data.get("city")
			user.address.country=form.cleaned_data.get("country")
			user.address.save()
			messages.info(request,"Address changed successfully")
			return redirect("ecommerce_platform:accounts")
		return redirect("ecommerce_platform:accounts")
	address_dict={
			"street_address": request.user.address.street_address,
			"postal_code": request.user.address.postal_code,
			"city": request.user.address.city,
			"country": request.user.address.country,
	}
	form=AddressChangeForm(initial=address_dict)
	context={
		"form":form,
	}
	return render(request,"address_change.html",context)