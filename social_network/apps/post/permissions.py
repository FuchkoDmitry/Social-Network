
from social_network.apps.user import schemas as user_schemas
from social_network.apps.post import schemas, models


def post_owner(owner: user_schemas.User, post: schemas.Post):
    return post.owner_id == owner.id
