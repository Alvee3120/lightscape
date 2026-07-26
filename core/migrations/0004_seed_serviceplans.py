from django.db import migrations


PLANS = [
    {
        'name': 'Editorial Day',
        'price': '1400.00',
        'unit': 'day',
        'order': 0,
        'features': [
            '8 hours on location',
            '40 graded frames',
            'Web + print licence',
            '72h turnaround',
        ],
    },
    {
        'name': 'Wedding Story',
        'price': '3200.00',
        'unit': 'event',
        'is_featured': True,
        'badge_text': 'Most booked',
        'order': 1,
        'features': [
            'Full-day coverage, two shooters',
            '400+ graded frames',
            'Private online gallery',
            'Hand-bound 40pp album',
        ],
    },
    {
        'name': 'Brand Campaign',
        'price': '5000.00',
        'price_prefix': 'From',
        'unit': 'project',
        'order': 2,
        'features': [
            'Concept + art direction',
            'Studio & location',
            'Retouched hero set',
            'Unlimited usage',
        ],
    },
]


def seed_plans(apps, schema_editor):
    ServicePlan = apps.get_model('core', 'ServicePlan')
    ServicePlanFeature = apps.get_model('core', 'ServicePlanFeature')

    if ServicePlan.objects.exists():
        return

    for plan_data in PLANS:
        features = plan_data.pop('features')
        plan = ServicePlan.objects.create(**plan_data)
        for i, text in enumerate(features):
            ServicePlanFeature.objects.create(plan=plan, text=text, order=i)


def remove_plans(apps, schema_editor):
    ServicePlan = apps.get_model('core', 'ServicePlan')
    ServicePlan.objects.filter(name__in=[p['name'] for p in PLANS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_serviceplan_serviceplanfeature'),
    ]

    operations = [
        migrations.RunPython(seed_plans, remove_plans),
    ]
