# Generated by Django 4.2.16 on 2024-10-24 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='password_reset_token',
            field=models.CharField(blank=True, default=None, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='token_expired_at',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]
