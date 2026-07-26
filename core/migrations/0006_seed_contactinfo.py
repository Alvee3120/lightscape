from django.db import migrations


def seed_contact_info(apps, schema_editor):
    ContactInfo = apps.get_model('core', 'ContactInfo')
    if not ContactInfo.objects.exists():
        ContactInfo.objects.create(
            studio_location='Pier 24, San Francisco, CA',
            email='hello@lumenatlas.studio',
            phone='+1 (415) 555-0184',
        )


def remove_contact_info(apps, schema_editor):
    ContactInfo = apps.get_model('core', 'ContactInfo')
    ContactInfo.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_contactinfo'),
    ]

    operations = [
        migrations.RunPython(seed_contact_info, remove_contact_info),
    ]
