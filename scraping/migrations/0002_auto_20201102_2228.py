# Generated by Django 3.1.3 on 2020-11-02 22:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraping', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Язык программиорвания')),
                ('slug', models.SlugField(blank=True, unique=True)),
            ],
            options={
                'verbose_name': 'Язык программирования',
                'verbose_name_plural': 'Языки программирования',
            },
        ),
        migrations.AlterModelOptions(
            name='city',
            options={'verbose_name': 'Город', 'verbose_name_plural': 'Города'},
        ),
        migrations.AlterField(
            model_name='city',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='city',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
    ]