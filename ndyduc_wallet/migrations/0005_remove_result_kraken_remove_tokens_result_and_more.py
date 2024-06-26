# Generated by Django 5.0.4 on 2024-05-05 11:56

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ndyduc_wallet', '0004_kraken_result_tokens'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='result',
            name='kraken',
        ),
        migrations.RemoveField(
            model_name='tokens',
            name='result',
        ),
        migrations.RenameField(
            model_name='inform',
            old_name='Content',
            new_name='content',
        ),
        migrations.RemoveField(
            model_name='inform',
            name='Datetime',
        ),
        migrations.RemoveField(
            model_name='inform',
            name='UserID',
        ),
        migrations.AddField(
            model_name='inform',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='ndyduc_wallet.user'),
        ),
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('flag', models.IntegerField()),
                ('wallet_id', models.CharField(max_length=100)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('currency', models.CharField(max_length=10)),
                ('to_id', models.CharField(max_length=100)),
                ('message', models.CharField(blank=True, max_length=255, null=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='ndyduc_wallet.user')),
            ],
        ),
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('public_key', models.CharField(max_length=100)),
                ('private_key', models.CharField(max_length=100)),
                ('wallet_id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='ndyduc_wallet.user')),
            ],
        ),
        migrations.CreateModel(
            name='Coins',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(max_length=50)),
                ('amount', models.DecimalField(decimal_places=10, max_digits=20)),
                ('wallet', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='ndyduc_wallet.wallet')),
            ],
        ),
        migrations.DeleteModel(
            name='Kraken',
        ),
        migrations.DeleteModel(
            name='Result',
        ),
        migrations.DeleteModel(
            name='Tokens',
        ),
        migrations.AddField(
            model_name='inform',
            name='datetime',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
