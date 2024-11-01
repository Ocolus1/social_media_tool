from .models import Post
import tweepy
from decouple import config
import logging


logger = logging.getLogger(__name__)


def post_to_twitter(post_id):
    try:
        logger.info(f"Post id - {post_id} {type(post_id)} started. Processing tweet. ")
        scheduled_post = Post.objects.get(id=post_id)
        twitter_account = scheduled_post.user.twitteraccount

        # Check if access token is valid, otherwise refresh it
        if not twitter_account:
            logger.error("Failed to get access token")
            raise Exception("Failed to get access token")

        logger.info("Access token acquired successfully.")

        client = tweepy.Client(
            consumer_key=config("TWITTER_CONSUMER_API_KEY"),
            consumer_secret=config("TWITTER_CONSUMER_API_KEY_SECRET"),
            access_token=twitter_account.access_token,
            access_token_secret=twitter_account.access_token_secret,
        )

        logger.info("Instantiated Twitter client.")

        try:
            client.create_tweet(text=scheduled_post.content)
            logger.info("Tweet posted successfully.")
            scheduled_post.status = "posted"
        except tweepy.TweepError as e:
            scheduled_post.status = "failed"
            logger.error(f"Tweepy Error posting tweet: {str(e)}")
        finally:
            scheduled_post.save()

        logger.info(f"Post Task ID: {scheduled_post.id} completed.")

    except Exception as e:
        logger.error(f"Error in post_to_twitter task: {str(e)} semi")
