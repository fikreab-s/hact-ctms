from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Feedback",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("username", models.CharField(blank=True, default="", max_length=150)),
                ("roles", models.CharField(blank=True, default="", help_text="Comma-separated snapshot of the submitter's roles.", max_length=255)),
                ("category", models.CharField(choices=[("bug", "Bug"), ("question", "Question"), ("suggestion", "Suggestion"), ("other", "Other")], default="bug", max_length=20)),
                ("severity", models.CharField(choices=[("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")], default="medium", max_length=20)),
                ("message", models.TextField()),
                ("page_url", models.CharField(blank=True, default="", max_length=1000)),
                ("user_agent", models.CharField(blank=True, default="", max_length=500)),
                ("screenshot", models.FileField(blank=True, null=True, upload_to="feedback/%Y/%m/")),
                ("status", models.CharField(choices=[("new", "New"), ("in_review", "In Review"), ("resolved", "Resolved"), ("wont_fix", "Won't Fix")], db_index=True, default="new", max_length=20)),
                ("admin_notes", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="feedback_items", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Feedback item",
                "verbose_name_plural": "Feedback items",
                "db_table": "feedback_items",
                "ordering": ["-created_at"],
            },
        ),
    ]
