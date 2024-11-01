from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from social_media.celery import app
import pytz


class Post(models.Model):
    TIMEZONE_CHOICES = [(tz, tz) for tz in pytz.all_timezones]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to="post_images/", null=True, blank=True)
    scheduled_time = models.DateTimeField(null=True, blank=True)
    timezone = models.CharField(
        max_length=50,
        choices=TIMEZONE_CHOICES,
        default="UTC",
        help_text="Timezone in which the scheduled time is set.",
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("scheduled", "Scheduled"),
            ("posted", "Posted"),
            ("failed", "Failed"),
        ],
        default="scheduled",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content

    def clean(self):
        # Ensure scheduled_time is in the future
        if self.scheduled_time and self.scheduled_time < timezone.now():
            raise ValidationError("The scheduled time must be in the future.")

    def save(self, *args, **kwargs):
        # Call the clean method to ensure validation
        self.clean()
        super().save(*args, **kwargs)

    def get_utc_scheduled_time(self):
        """Convert scheduled_time to UTC based on the selected timezone."""
        if self.scheduled_time and self.timezone:
            tz = pytz.timezone(self.timezone)
            localized_time = tz.localize(self.scheduled_time)
            return localized_time.astimezone(pytz.utc)
        return None

    def schedule_post(self):
        # Use the converted UTC time for scheduling
        utc_scheduled_time = self.get_utc_scheduled_time()
        if utc_scheduled_time:
            app.send_task("post_to_twitter", args=[self.id], eta=utc_scheduled_time)
