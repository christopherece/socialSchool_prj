# Generated by Django 5.2.3 on 2025-07-01 08:42

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_comment_updated_at'),
        ('user_notifications', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='expires_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='group_id',
            field=models.CharField(blank=True, max_length=36, null=True),
        ),
        migrations.AddField(
            model_name='notification',
            name='priority',
            field=models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='medium', max_length=10),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['recipient', 'is_read'], name='user_notifi_recipie_1ce727_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['created_at'], name='user_notifi_created_6c476a_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['deleted_at'], name='user_notifi_deleted_e3a93e_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['group_id'], name='user_notifi_group_i_e6d013_idx'),
        ),
    ]
