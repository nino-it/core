# Generated by Django 4.2.17 on 2024-12-09 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200)),
                ('text', models.TextField()),
                ('category', models.CharField(max_length=100)),
                ('priority', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '7'), (8, '8'), (9, '9'), (10, '10')])),
                ('time_entry', models.DateTimeField(auto_now_add=True)),
                ('time_edit', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.DeleteModel(
            name='Item',
        ),
    ]
