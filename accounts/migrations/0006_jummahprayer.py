# Generated by Django 5.0.1 on 2024-07-01 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_iqamahadjustment_prayer_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='JummahPrayer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('location', models.CharField(max_length=255)),
            ],
        ),
    ]
