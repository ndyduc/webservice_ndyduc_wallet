# Generated by Django 5.0.4 on 2024-04-26 17:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ndyduc_wallet', '0003_inform'),
    ]

    operations = [
        migrations.CreateModel(
            name='Kraken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('error', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kraken', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='result', to='ndyduc_wallet.kraken')),
            ],
        ),
        migrations.CreateModel(
            name='Tokens',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ask', models.FloatField(blank=True, null=True)),
                ('bid', models.FloatField(blank=True, null=True)),
                ('close', models.FloatField(blank=True, null=True)),
                ('volume', models.FloatField(blank=True, null=True)),
                ('averageprice', models.FloatField(blank=True, null=True)),
                ('numberoftrades', models.FloatField(blank=True, null=True)),
                ('low', models.FloatField(blank=True, null=True)),
                ('high', models.FloatField(blank=True, null=True)),
                ('open', models.FloatField(blank=True, null=True)),
                ('result', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='tokens', to='ndyduc_wallet.result')),
            ],
        ),
    ]
