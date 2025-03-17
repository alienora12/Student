# Generated by Django 5.1.7 on 2025-03-17 04:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_user_university'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Course Name')),
                ('credits', models.IntegerField(verbose_name='Credits')),
                ('professor', models.CharField(blank=True, max_length=200, null=True, verbose_name='Professor')),
                ('type', models.CharField(choices=[('mandatory', 'Mandatory'), ('optional', 'Optional')], default='mandatory', max_length=20)),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('university', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses', to='myapp.university', verbose_name='University')),
            ],
            options={
                'verbose_name': 'Course',
                'verbose_name_plural': 'Courses',
                'ordering': ['name'],
            },
        ),
    ]
