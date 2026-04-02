import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Add user FK to Order (nullable so existing rows are preserved)
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='orders',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        # Add tenant FK to Order (nullable so existing rows are preserved)
        migrations.AddField(
            model_name='order',
            name='tenant',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='orders',
                to='users.tenant',
            ),
        ),
        # Make Order.name nullable (was required; kept for invoice display only)
        migrations.AlterField(
            model_name='order',
            name='name',
            field=models.CharField(
                blank=True,
                max_length=254,
                null=True,
                verbose_name='Customer Name',
            ),
        ),
        # Remove Subscription.active (per-tenant state moves to TenantSubscription)
        migrations.RemoveField(
            model_name='subscription',
            name='active',
        ),
        # New TenantSubscription model
        migrations.CreateModel(
            name='TenantSubscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                (
                    'tenant',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='subscriptions',
                        to='users.tenant',
                    ),
                ),
                (
                    'plan',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='tenant_subscriptions',
                        to='users.subscription',
                    ),
                ),
                (
                    'order',
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='tenant_subscription',
                        to='users.order',
                    ),
                ),
            ],
        ),
    ]
