from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
#from star_ratings.models import Rating
import uuid
from django.urls import reverse
from django.utils.text import slugify
from django_countries.fields import CountryField
from phone_field import PhoneField


class Category(models.Model):
	name=models.CharField(max_length=20)
	class Meta:
		verbose_name_plural="Categories"
	def __str__(self):
		return self.name


class Address(models.Model):
	user=models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
	street_address=models.CharField(max_length=20,default="")
	postal_code=models.CharField(max_length=7,default="00000")
	city=models.CharField(max_length=14,default="")
	country=models.CharField(max_length=8,default="")

class User_Profile(models.Model):
	user=models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
	gender=models.CharField(max_length=8,default="")
	phone_number=PhoneField(blank=True, help_text='Contact phone number')
	#address=models.OneToOneField(Address,on_delete=models.SET_NULL,null=True)

class Product(models.Model):
	name=models.CharField(max_length=50)
	manufacturer=models.CharField(max_length=50,default="")
	units_available=models.PositiveIntegerField(null=True)
	price=models.FloatField(null=True)
	description=models.TextField()
	image=models.ImageField(upload_to ='images', default = 'images/none/no-image.png')
	added_on=models.DateTimeField(auto_now_add=True)
	slug=models.SlugField(default="", editable=False, max_length=50, null = False)
	categories=models.ManyToManyField(Category)
	#ratings = GenericRelation(Rating, related_query_name="products")
	"""CATEGORIES=(
			("SMARTPHONES","SMARTPHONES"),
			("CLOTHING","CLOTHING"),
			("HOME APPLIANCES","HOME APPLIANCES"),
			("COMPUTING","COMPUTING")
		)
	category = models.CharField(
        max_length=20,
        choices=CATEGORIES,
        blank=True,
        default='',
        help_text='Product Category'
    )"""

	def __str__(self):
		return self.name
	class Meta:
		ordering=["-added_on"]
	def get_absolute_url(self):
		return reverse("ecommerce_platform:product_detail",kwargs={
			"slug":self.slug
			}
			)
	def get_add_to_cart_url(self):
		return reverse("ecommerce_platform:add_to_cart",kwargs={
			"slug":self.slug
			}
			)
	def get_remove_from_cart_url(self):
		return reverse("ecommerce_platform:remove_from_cart",kwargs={
			"slug":self.slug
			}
			)
	def save(self,*args,**kwargs):
		value=self.name
		self.slug=slugify(value,allow_unicode=True)
		super().save(*args,**kwargs)

class Comment(models.Model):
	author=models.CharField(max_length=10)
	body=models.TextField()
	created_on=models.DateTimeField(auto_now_add=True)
	product=models.ForeignKey(Product,on_delete=models.CASCADE)
			

class OrderItem(models.Model):
	user=models.ForeignKey(User,on_delete=models.CASCADE)
	order_number=models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique Order Number for this Product')
	product=models.ForeignKey(Product,on_delete=models.CASCADE)
	order_invoice_code=models.CharField(max_length=10,blank=True,null=True)
	ordered=models.BooleanField(default=False)
	quantity=models.IntegerField(default=1)
	created_on=models.DateTimeField(auto_now_add=True)
	ordered_date=models.DateTimeField(null=True)
	delivered=models.BooleanField(default=False)
	can_comment=models.BooleanField(default=False)
	can_rate=models.BooleanField(default=False)
	order_item_total=models.FloatField(null=True)
	address=models.CharField(max_length=200,null=True)
	payment_type=models.CharField(max_length=20,null=True)
	commented=models.BooleanField(default=False)
	rated=models.BooleanField(default=False)
	def get_total(self):
		return self.product.price*self.quantity
	def __str__(self):
		return self.product.name + ":" + str(self.quantity)

class Coupon(models.Model):
	#users=models.ManyToManyField(User)
	code=models.CharField(max_length=5)
	discount=models.FloatField(null=True)
	valid_from=models.DateTimeField(null=True)
	valid_to=models.DateTimeField(null=True)
	min_amount=models.FloatField(null=True)
	active=models.BooleanField(default=True)
	def __str__(self):
		return self.code

class Cart(models.Model):
	user=models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
	order_items=models.ManyToManyField(OrderItem)
	#cart_total=models.FloatField(null=True)
	invoice_code=models.CharField(max_length=20,blank=True,null=True)
	#coupon=models.ForeignKey(Coupon,on_delete=models.SET_NULL,blank=True,null=True)
	def get_total(self):
		total=0
		for item in self.order_items.all():
			total+=(item.product.price)*item.quantity
		return total
	def get_total_after_discount(self,amount):
		total=0
		for item in self.order_items.all():
			total+=(item.product.price)*item.quantity
		total-=amount
		return total




