# Generated for HACT CTMS — per-study SENAITE Client title.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinical', '0005_item_openclinica_oids'),
    ]

    operations = [
        migrations.AddField(
            model_name='study',
            name='senaite_client_title',
            field=models.CharField(
                blank=True,
                default='HACT Clinical Trials',
                help_text=(
                    "SENAITE Client title this study's samples/results live under. "
                    "Sample push and result pull are scoped to this Client so multiple "
                    "studies/labs can be onboarded independently."
                ),
                max_length=255,
            ),
        ),
    ]
