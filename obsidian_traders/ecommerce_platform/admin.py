from django.contrib import admin
from .models import Product,OrderItem,Coupon,Cart,Category

class CouponAdmin(admin.ModelAdmin):
	list_display=['code','valid_from','valid_to','discount','active']
	list_filter=['valid_from','valid_to','active']
	search_fields=['code']

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(OrderItem)
admin.site.register(Coupon,CouponAdmin)
admin.site.register(Cart)
