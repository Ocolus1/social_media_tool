from ninja import Router, UploadedFile, Form, File
from django.utils import timezone
from .models import Post
from .schema import PostCreateSchema
from django.shortcuts import get_object_or_404
from typing import Optional
from django.http import JsonResponse
from datetime import datetime
import logging
from django_q.models import Schedule
import pytz

logger = logging.getLogger(__name__)
router = Router()


@router.post("/")
def create_post(
    request,
    image_file: Optional[UploadedFile] = File(None),
    payload: PostCreateSchema = Form(...),
):
    # Parse and validate the scheduled time
    try:
        scheduled_time = datetime.strptime(payload.scheduled_time, "%Y-%m-%d %H:%M")
    except ValueError:
        return JsonResponse(
            {"error": "Invalid time format. Use 'YYYY-MM-DD HH:MM'."}, status=400
        )

    local_timezone = pytz.timezone(payload.timezone)

    # Localize to the local timezone to make it timezone-aware
    localized_datetime = local_timezone.localize(scheduled_time)

    # Convert to UTC timezone
    utc_datetime = localized_datetime.astimezone(pytz.utc)

    # Check if scheduled time is in the future
    if utc_datetime < timezone.now():
        return JsonResponse(
            {"error": "Scheduled time must be in the future"}, status=400
        )

    aware_time = timezone.make_aware(scheduled_time)
    # Create the post
    scheduled_post = Post.objects.create(
        user=request.user,
        content=payload.content,
        scheduled_time=aware_time,  # Store in UTC
        image=image_file if image_file else None,
    )

    # Schedule the task using the UTC time
    Schedule.objects.create(
        func="posts.tasks.post_to_twitter",
        name=f"Post to Twitter {scheduled_post.id}",
        hook="hooks.print_result",
        args=scheduled_post.id,
        repeats=1,
        schedule_type=Schedule.ONCE,
        next_run=utc_datetime,  # Ensure this is in UTC
    )

    logger.info(f"Scheduled post for post id - {scheduled_post.id}")

    return JsonResponse({"id": scheduled_post.id, "status": "created"})


@router.get("/{post_id}/")
def retrieve_post(request, post_id: int):
    """Retrieve a specific post by ID."""
    post = get_object_or_404(Post, id=post_id)
    return {
        "id": post.id,
        "content": post.content,
        "status": post.status,
        "scheduled_time": post.scheduled_time,
        "image": post.image.url if post.image else None,
        "created_at": post.created_at,
    }


@router.get("/")
def list_posts(request):
    """List all posts ordered by scheduled time."""
    posts = Post.objects.all().order_by("scheduled_time")
    return [
        {"id": post.id, "content": post.content, "scheduled_time": post.scheduled_time}
        for post in posts
    ]


@router.delete("/{post_id}/")
def delete_post(request, post_id: int):
    """Delete a specific post by ID."""
    post = get_object_or_404(Post, id=post_id)
    post.delete()
    return {"status": "deleted"}
