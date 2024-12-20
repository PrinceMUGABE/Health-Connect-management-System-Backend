# Generated by Django 5.0.7 on 2024-10-24 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ExamResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_marks', models.PositiveIntegerField(default=0)),
                ('status', models.CharField(choices=[('failed', 'Failed'), ('succeeded', 'Succeeded')], default='failed', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
