# Generated by Django 4.2.17 on 2024-12-19 16:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_rating'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostAverageRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('average_rating', models.FloatField(default=0.0)),
                ('total_ratings', models.IntegerField(default=0)),
                ('total_score', models.IntegerField(default=0)),
                ('post', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='average_rating_entry', to='posts.post')),
            ],
        ),
    ]
