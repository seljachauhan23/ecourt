# Generated by Django 5.1.3 on 2025-01-23 04:47

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Case',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('case_number', models.CharField(max_length=50, unique=True)),
                ('case_title', models.CharField(max_length=255)),
                ('case_type', models.CharField(max_length=50)),
                ('case_description', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('ACTIVE', 'Active'), ('DISMISSED', 'Dismissed'), ('CLOSED', 'Closed')], default='PENDING', max_length=20)),
                ('lawyer_accepted', models.BooleanField(null=True)),
                ('defendant_lawyer_accepted', models.BooleanField(null=True)),
                ('case_filed_date', models.DateTimeField(auto_now_add=True)),
                ('verdict_date', models.DateField(null=True)),
                ('verdict_time', models.TimeField(null=True)),
                ('verdict', models.TextField(null=True)),
                ('assigned_judge', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cases', to='users.judge')),
                ('assigned_lawyer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cases', to='users.lawyer')),
                ('defendant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='defendant_cases', to='users.citizen')),
                ('defendant_lawyer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='defendent_lawyer', to='users.lawyer')),
                ('plaintiff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plaintiff_cases', to='users.citizen')),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_type', models.CharField(max_length=100)),
                ('file', models.FileField(upload_to='case_documents/%Y/%m/%d/')),
                ('user_type', models.CharField(max_length=15, null=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='case_documents', to='cases.case')),
                ('uploaded_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='uploaded_by')),
            ],
        ),
        migrations.CreateModel(
            name='Hearing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('status', models.CharField(default='Scheduled', max_length=50)),
                ('videocall_link', models.CharField(blank=True, max_length=150, null=True)),
                ('outcome', models.TextField(blank=True, null=True)),
                ('assigned_judge', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.judge')),
                ('case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hearings', to='cases.case')),
            ],
        ),
    ]
