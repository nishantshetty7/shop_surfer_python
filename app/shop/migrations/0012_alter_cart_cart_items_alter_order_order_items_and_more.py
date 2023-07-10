# Generated by Django 4.2.2 on 2023-07-09 16:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0011_remove_product_category_alter_product_rating_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='cart_items',
            field=models.ManyToManyField(related_name='cart_items', through='shop.CartItem', to='shop.product'),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_items',
            field=models.ManyToManyField(related_name='order_items', through='shop.OrderItem', to='shop.product'),
        ),
        migrations.CreateModel(
            name='TopCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_purchases', models.IntegerField(default=0)),
                ('category', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='shop.category')),
            ],
        ),
    ]
