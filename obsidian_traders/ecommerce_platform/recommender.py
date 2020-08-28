import redis
from django.conf import settings
from .models import Product

r = redis.StrictRedis(host=settings.REDIS_HOST,
					port=settings.REDIS_PORT,
					db=settings.REDIS_DB)

class Recommender(object):
	def get_product_key(self,id):
		return "product:{}:purchased_with".format(id)

	def products_bought(self,products):
		product_ids=[p.id for p in products]
		for product_id in product_ids:
			for with_id in product_ids:
				#get the other products bought with each product
				if product_id!=with_id:
					#increment score for product purchased together
					r.zincrby(self.get_product_key(product_id),1,with_id)

	def suggest_products_for(self,products,max_results=6):
		product_ids=[p.id for p in products]
		if len(products)==1:
			#only 1 product
			suggestions=r.zrange(self.get_product_key(product_ids[0]),0,-1,desc=True)[:max_results]

		else:
			#generate a temporary key
			flat_ids="".join([str(id) for ids in product_ids])
			tmp_key="tmp_{}".format(flat_ids)
			#multiple products,combine scores for all products
			#store the resulting sorted set in a temporary key
			keys=[self.get_product_key(id) for id in product_ids]
			r.zunionstore(tmp_key,keys)
			#remove ids for the products the recommendation is for
			r.zrem(tmp_key,*product_ids)
			#get the product ids by their score, descendant sort
			suggestions=r.zrange(tmp_key,0,-1,desc=True)[:max_results]
			#remove the temporary key
			r.delete(tmp_key)
		suggested_product_ids=[int(id) for id in suggestions]

		#get suggested products and sort by order of appearance
		suggested_product=list(Product.objects.filter(id__in=suggested_product_ids))
		suggested_product.sort(key=lambda x:suggested_product_ids.index(x.id))
		return suggested_product

	def clear_purchases(self):
		for id in Product.objects.values_list(id,flat=True):
			r.delete((self.get_product_key(id)))