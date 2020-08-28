from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import Form
from phone_field.forms import PhoneFormField

COUNTRIES=(
		("KENYA","KENYA"),
		("TANZANIA","TANZANIA"),
		("UGANDA","UGANDA")
		)

class SignUpForm(UserCreationForm):
	GENDER=(
		("MALE","MALE"),
		("FEMALE","FEMALE"),
		("OTHER","OTHER")
		)
	first_name=forms.CharField(max_length=30,required=True,help_text="Required.")
	last_name=forms.CharField(max_length=30,required=True,help_text="Required.")
	phone_number=PhoneFormField(required=True,help_text="Phone Number including country code")
	email=forms.EmailField(max_length=254,required=True,help_text="Required. Fill a valid email address")
	gender=forms.ChoiceField(
		choices=GENDER,
		required=True
		)
	street_address=forms.CharField(max_length=20,required=True,help_text="Required.")
	postal_code=forms.CharField(max_length=7,required=True,help_text="Postal Code,Numbers only.")
	city=forms.CharField(max_length=14,required=True,help_text="Required.")
	country=forms.ChoiceField(
		choices=COUNTRIES,
		required=True
		)
	class Meta:
		model=User
		fields=("username","first_name","last_name","gender","street_address","postal_code","city","country","phone_number","email","password1","password2")

class UpdateQuantityForm(Form):
	PRODUCT_QUANTITY_CHOICES=[(i,str(i)) for i in range(1,21)]
	quantity=forms.TypedChoiceField(
		choices=PRODUCT_QUANTITY_CHOICES,
		coerce=int,
		label="")

class CommentForm(forms.Form):
	author=forms.CharField(
		max_length=10,
		widget=forms.TextInput(attrs={
			"class":"form-'control",
			"placeholder":" Your Name"
			})
		)
	body=forms.CharField(
		widget=forms.Textarea(attrs={
			"class":"form-control",
			"placeholder":"Leave a comment!"
			})
		)


class CheckOutForm(Form):
	DELIVERY_METHODS=(
		("Delivery to Home or Office","Delivery to Home or Office"),
		("Pick Up Station","Pick Up Station")
		)
	PICK_UP_STATIONS=(
		("Room 23,First Floor,Kemu Towers,Nairobi,Kenya","Room 23,First Floor,Kemu Towers,Nairobi,Kenya"),
		("Kikuyu Matatu Stage,Kikuyu,Kiambu","Kikuyu Matatu Stage,Kikuyu,Kiambu")
		)
	SHIPPING_ADDRESSES=(
		("Use Default Shipping Address","Use Default Shipping Address"),
		("Set New Shipping Address","Set New Shipping Address")
		)
	delivery_method=forms.ChoiceField(choices=DELIVERY_METHODS,required=True)
	pick_up_station=forms.ChoiceField(choices=PICK_UP_STATIONS)
	#avail_pick_up_stations=forms.ChoiceField(choices=PICK_UP_STATIONS,required=False)
	#use_default_shipping_address=forms.BooleanField(required=False)
	shipping_address=forms.ChoiceField(choices=SHIPPING_ADDRESSES)
	street_address=forms.CharField(max_length=20,required=False)
	postal_code=forms.CharField(max_length=7,required=False,help_text="Postal Code,Numbers only.")
	city=forms.CharField(max_length=14,required=False)
	country=forms.ChoiceField(
		choices=COUNTRIES
		)
	PAYMENT_CHOICES=(
		("PayPal","PayPal"),
		("Stripe","Stripe")
		)
	payment_option=forms.ChoiceField(choices=PAYMENT_CHOICES)

class CouponForm(Form):
	code=forms.CharField(label="Do you have a valid voucher?",max_length=5)

class AccountDetailsChangeForm(Form):
	first_name=forms.CharField(max_length=30,required=True,help_text="Required.")
	last_name=forms.CharField(max_length=30,required=True,help_text="Required.")
	phone_number=PhoneFormField(required=True,help_text="Phone Number including country code")
	email=forms.EmailField(max_length=254,required=True,help_text="Required. Fill a valid email address")

class AddressChangeForm(Form):
	street_address=forms.CharField(max_length=20,required=True,help_text="Required.")
	postal_code=forms.CharField(max_length=7,required=True,help_text="Postal Code,Numbers only.")
	city=forms.CharField(max_length=14,required=True,help_text="Required.")
	country=forms.ChoiceField(
		choices=COUNTRIES,
		required=True
		)