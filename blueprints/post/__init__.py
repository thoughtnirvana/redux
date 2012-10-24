from lib import utils
from config import settings

BEFORE_REQUESTS = [utils.http_auth(settings.HTTP_USERNAME, settings.HTTP_PASSWORD,
                                   'post.new', 'post.delete', 'post.edit', 'post.comment_delete')]
