# Generated by Django 2.2.3 on 2019-07-26 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0002_auto_20190726_1053'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cardtypemap',
            name='card',
        ),
        migrations.RemoveField(
            model_name='cardtypemap',
            name='type',
        ),
        migrations.AddField(
            model_name='card',
            name='types',
            field=models.ManyToManyField(to='cards.Type'),
        ),
        migrations.AddField(
            model_name='set',
            name='cards',
            field=models.ManyToManyField(to='cards.Card'),
        ),
        migrations.DeleteModel(
            name='CardSetMap',
        ),
        migrations.DeleteModel(
            name='CardTypeMap',
        ),
    ]
