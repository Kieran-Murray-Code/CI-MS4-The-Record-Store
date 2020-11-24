# Generated by Django 3.1.2 on 2020-11-23 19:07

from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('profiles', '0001_initial'),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_number', models.CharField(editable=False, max_length=32)),
                ('email', models.EmailField(max_length=254, verbose_name='Email')),
                ('first_name', models.CharField(max_length=50, verbose_name='First Name')),
                ('last_name', models.CharField(max_length=50, verbose_name='Last Name')),
                ('address_line_1', models.CharField(max_length=80, verbose_name='Address Line 1')),
                ('address_line_2', models.CharField(max_length=80, verbose_name='Address Line 2')),
                ('town_or_city', models.CharField(max_length=80, verbose_name='City/Town')),
                ('county_or_province', models.CharField(max_length=80, verbose_name='County/Province')),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('post_code_or_zip_code', models.CharField(max_length=80, verbose_name='Postcode/Zip')),
                ('phone_number', models.CharField(max_length=20, verbose_name='Phone')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('delivery_cost', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('order_total', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('grand_total', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('user_profile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='profiles.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='OrderLineItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=0)),
                ('line_item_total', models.DecimalField(decimal_places=2, editable=False, max_digits=6)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='line_items', to='checkout.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product')),
            ],
        ),
    ]