# Generated by Django 3.0.3 on 2020-08-21 07:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce_platform', '0027_user_profile_phone_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='coupon',
        ),
        migrations.AddField(
            model_name='cart',
            name='coupon',
            field=models.ManyToManyField(to='ecommerce_platform.Coupon'),
        ),
    ]