from pydantic import BaseModel, field_validator
from datetime import datetime
from django.utils import timezone as tm


class PostCreateSchema(BaseModel):
    content: str
    scheduled_time: str
    timezone: str

    @field_validator("scheduled_time")
    def validate_scheduled_time(cls, value):
        try:
            # Convert to datetime
            scheduled_time = datetime.strptime(value, "%Y-%m-%d %H:%M")
            # Make it timezone-aware
            scheduled_time = tm.make_aware(scheduled_time)
            if scheduled_time < tm.now():
                raise ValueError("Scheduled time must be in the future.")
            return value  # Return as str, only if needed in this format
        except Exception:
            raise ValueError('Invalid time format. Use "YYYY-MM-DD HH:MM".')
