# Generated by Django 4.2.2 on 2023-07-02 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_user_auth_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='image',
            field=models.ImageField(blank=True, default='', upload_to='user/'),
        ),
    ]
