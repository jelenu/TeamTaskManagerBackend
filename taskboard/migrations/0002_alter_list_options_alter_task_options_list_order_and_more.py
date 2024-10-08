# Generated by Django 5.1.1 on 2024-09-09 14:13

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taskboard', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='list',
            options={'ordering': ['order']},
        ),
        migrations.AlterModelOptions(
            name='task',
            options={'ordering': ['order']},
        ),
        migrations.AddField(
            model_name='list',
            name='order',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='task',
            name='order',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='task',
            name='assigned',
            field=models.ManyToManyField(blank=True, related_name='assigned_tasks', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='list',
            unique_together={('board', 'order')},
        ),
        migrations.AlterUniqueTogether(
            name='task',
            unique_together={('list', 'order')},
        ),
    ]
