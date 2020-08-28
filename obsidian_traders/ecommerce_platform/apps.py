from django.apps import AppConfig


class EcommercePlatformConfig(AppConfig):
    name = 'ecommerce_platform'

    def ready(self):
    	import ecommerce_platform.signals