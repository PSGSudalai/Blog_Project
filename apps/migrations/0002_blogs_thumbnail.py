# Generated by Django 4.2.7 on 2024-07-19 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogs',
            name='thumbnail',
            field=models.ImageField(default=1, upload_to='images/'),
            preserve_default=False,
        ),
    ]
