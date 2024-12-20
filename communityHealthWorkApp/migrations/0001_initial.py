# Generated by Django 5.0.7 on 2024-10-24 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CommunityHealthWorker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(default='', max_length=50)),
                ('middle_name', models.CharField(blank=True, max_length=50, null=True)),
                ('last_name', models.CharField(default='', max_length=50)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('address', models.CharField(default='', max_length=255)),
                ('status', models.CharField(choices=[('accepted', 'Accepted'), ('rejected', 'Rejected')], default='accepted', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
