from ninja import Router
from django.contrib.auth.models import User
from django.http import HttpRequest
import tweepy
from decouple import config
from .models import TwitterAccount
from .schema import RegisterSchema, UpdateProfileSchema, Error, Success
import requests
from urllib.parse import parse_qs


TWITTER_REDIRECT_URI = config("TWITTER_REDIRECT_URI")
TWITTER_CONSUMER_API_KEY = config("TWITTER_CONSUMER_API_KEY")
TWITTER_CONSUMER_API_KEY_SECRET = config("TWITTER_CONSUMER_API_KEY_SECRET")

router = Router()


#  Retrieve all registered users
@router.get("/")
def get_users(request):
    """
    Retrieve all registered users.

    This function retrieves all user records from the database and returns them as a list.

    Parameters:
    request (Request): The incoming request object containing any necessary data.

    Returns:
    List[Dict]: A list of dictionaries representing all registered users.
    """
    # # Set `next_run` to a timezone-aware datetime
    # next_run_time = timezone.now() + timedelta(minutes=4)

    # ero = Schedule.objects.create(
    #     func='posts.tasks.post_to_twitter',
    #     hook='hooks.print_result',
    #     args='123',  # Example argument
    #     repeats=1,
    #     schedule_type=Schedule.ONCE,
    #     next_run=next_run_time  # Now properly timezone-aware
    # )
    # print(f"Task ID: {ero}")

    users = User.objects.all().values("id", "username", "email")
    return list(users)


# Define a route for the root endpoint using an HTTP POST method to handle user registration
@router.post("/", auth=None)
def register_user(request: HttpRequest, payload: RegisterSchema):
    """
    Registers a new user in the system.

    This function handles user registration by creating a new user record
    in the database. It first checks if the desired username already exists.
    If the username is available, it creates the user with the provided
    username, password, and email from the `payload`.

    Parameters:
    - request: The HTTP request object containing metadata about the request.
    - payload (RegisterSchema): An object containing the data needed for
      registration, including `username`, `password`, and `email`.

    Returns:
    - dict: A dictionary containing either a success message and user details,
      or an error message if the username is already taken.
    """
    # Check if a user with the given username already exists in the database
    if User.objects.filter(username=payload.username).exists():
        return {"error": "Username already taken"}

    # Create a new user in the database with the provided username, password, and email
    user = User.objects.create_user(
        username=payload.username, password=payload.password, email=payload.email
    )

    # Return a success message along with the newly registered user's details
    return {"success": "User registered successfully", "user": user}


# Update user profile (requires JWT authentication)
# Define a route for the 'update-profile' endpoint using an HTTP PUT method and require authentication via AuthBearer
@router.put("/update-profile")
def update_profile(request: HttpRequest, payload: UpdateProfileSchema):
    # Retrieve the authenticated user from the request
    user = request.auth

    # Update user's username if the payload contains a new username
    if payload.username:
        user.username = payload.username

    # Update user's email if the payload contains a new email
    if payload.email:
        user.email = payload.email

    # Update user's password if the payload contains a new password
    if payload.password:
        user.set_password(payload.password)

    # Save the updated user information to the database
    user.save()

    # Return a success message after updating the profile
    return {"success": "Profile updated successfully"}


# Define a route for the 'delete-user' endpoint using an HTTP DELETE method and require authentication via AuthBearer
@router.delete("/delete-user")
def delete_user(request: HttpRequest):
    # Retrieve the authenticated user from the request
    user = request.auth

    # Delete the user account from the database
    user.delete()

    # Return a success message after deleting the user account
    return {"success": "User deleted successfully"}


@router.get("/social/twitter-login")
def twitter_login(request: HttpRequest):
    """
    Initiates Twitter OAuth 1.0a authentication by redirecting the user to Twitter's authorization page.
    """
    if request.user.is_authenticated:
        oauth1_user_handler = tweepy.OAuth1UserHandler(
            config("TWITTER_CONSUMER_API_KEY"),
            config("TWITTER_CONSUMER_API_KEY_SECRET"),
            callback=config("TWITTER_REDIRECT_URI"),
        )

        try:
            authorization_url = oauth1_user_handler.get_authorization_url(
                signin_with_twitter=True
            )

            # Store the request token and user ID in the session
            request.session["oauth_token"] = oauth1_user_handler.request_token[
                "oauth_token"
            ]
            request.session["oauth_token_secret"] = oauth1_user_handler.request_token[
                "oauth_token_secret"
            ]
            request.session["user_id"] = (
                request.user.id
            )  # Store user ID instead of entire user object

            return {"authorization_url": authorization_url}
        except tweepy.TweepyException as e:
            return 400, {"error": f"Failed to initiate Twitter login: {str(e)}"}
    else:
        return 400, {"error": "User must be logged in to initiate Twitter login."}


@router.get("/social/twitter-callback", auth=None, response={400: Error, 200: Success})
def twitter_callback(request: HttpRequest):
    """
    Handles Twitter's callback after user authorization, exchanges the authorization code for access tokens,
    and saves these tokens to the database.
    """
    oauth_verifier = request.GET.get("oauth_verifier")
    oauth_token = request.GET.get("oauth_token")

    if not oauth_verifier:
        return 400, {"error": "Missing OAuth verifier from Twitter callback"}

    # Validate that the request token matches the session token
    session_oauth_token = request.session.get("oauth_token")

    if oauth_token != session_oauth_token:
        return 400, {"error": "Token mismatch. Authentication failed."}

    try:
        # Exchange the temporary tokens for access tokens
        response = requests.post(
            url="https://api.twitter.com/oauth/access_token",
            data={
                "oauth_consumer_key": config("TWITTER_CONSUMER_API_KEY"),
                "oauth_token": session_oauth_token,
                "oauth_verifier": oauth_verifier,
            },
        )

        if response.status_code == 200:
            response_data = parse_qs(response.text)
            access_token = response_data["oauth_token"][0]
            access_token_secret = response_data["oauth_token_secret"][0]

            # Clear the session tokens after successful authentication
            del request.session["oauth_token"]
            del request.session["oauth_token_secret"]

            # Retrieve and delete the user ID from the session
            user_id = request.session.pop("user_id", None)

            if user_id:
                user = User.objects.get(id=user_id)
                twitter_account, _ = TwitterAccount.objects.get_or_create(user=user)
                twitter_account.access_token = access_token
                twitter_account.access_token_secret = access_token_secret
                twitter_account.save()

                return 200, {"message": "User Twitter account connected successfully!"}
            else:
                return 400, {"error": "User is not authenticated"}

        else:
            return 400, {"error": "Failed to connect to Twitter account"}

    except tweepy.TweepyException as e:
        return 400, {"error": f"Failed to get access token: {str(e)}"}
