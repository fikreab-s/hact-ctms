# Generated for HACT CTMS — add OpenClinica OID fields to Item so CRFs
# imported from OpenClinica's ODM metadata can round-trip data back reliably.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinical', '0004_study_openclinica_study_identifier'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='openclinica_item_oid',
            field=models.CharField(
                blank=True,
                default='',
                help_text="OpenClinica ItemDef OID, e.g. 'I_SCREE_WEIGHT'.",
                max_length=100,
            ),
        ),
        migrations.AddField(
            model_name='item',
            name='openclinica_item_group_oid',
            field=models.CharField(
                blank=True,
                default='',
                help_text="OpenClinica ItemGroupDef OID that contains this item, e.g. 'IG_SCREE_UNGRP'.",
                max_length=100,
            ),
        ),
    ]
