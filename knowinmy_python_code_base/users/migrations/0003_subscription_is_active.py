from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_order_tenant_order_user_tenantsubscription_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
