# Generated by Django 4.2.17 on 2024-12-26 22:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0006_bill_billspec'),
    ]

    operations = [
        migrations.AddField(
            model_name='billspec',
            name='label',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='billspec',
            name='name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='billspec',
            name='quantity',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='billspec',
            name='tax_base_amnt',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='billspec',
            name='total',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='billspec',
            name='unit_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='billspec',
            name='vat',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]
