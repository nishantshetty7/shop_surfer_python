# Generated by Django 4.2.2 on 2023-06-30 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_user_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='image',
            field=models.ImageField(default='', upload_to='user/'),
        ),
    ]