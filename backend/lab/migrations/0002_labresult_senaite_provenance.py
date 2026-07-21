# Generated for HACT CTMS — SENAITE provenance on LabResult (idempotent pull).

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lab', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='labresult',
            name='senaite_sample_id',
            field=models.CharField(
                blank=True,
                db_index=True,
                default='',
                help_text="Source SENAITE AnalysisRequest ID (e.g. 'WS-0001').",
                max_length=100,
            ),
        ),
        migrations.AddField(
            model_name='labresult',
            name='senaite_analysis_uid',
            field=models.CharField(
                blank=True,
                db_index=True,
                default='',
                help_text="Source SENAITE Analysis UID — unique per result, used for de-duplication.",
                max_length=64,
            ),
        ),
    ]
