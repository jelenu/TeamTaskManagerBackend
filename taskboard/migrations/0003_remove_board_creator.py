# Generated by Django 5.1.1 on 2024-09-12 17:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('taskboard', '0002_alter_list_options_alter_task_options_list_order_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='board',
            name='creator',
        ),
    ]
