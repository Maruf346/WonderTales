from django.db import migrations

def update_site(apps, schema_editor):
    try:
        Site = apps.get_model('sites', 'Site')
        Site.objects.update_or_create(
            id=1,
            defaults={
                'domain': 'api.wondertales.com',
                'name': 'Chef Starz'
            }
        )
    except Exception:
        pass

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_customusermodel_options'),
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(update_site),
    ]
