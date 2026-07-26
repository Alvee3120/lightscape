from django.db import migrations


def seed_content(apps, schema_editor):
    SiteContent = apps.get_model('core', 'SiteContent')
    if not SiteContent.objects.exists():
        SiteContent.objects.create(heading='About LightScape')


def remove_content(apps, schema_editor):
    SiteContent = apps.get_model('core', 'SiteContent')
    SiteContent.objects.filter(heading='About LightScape').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_content, remove_content),
    ]
