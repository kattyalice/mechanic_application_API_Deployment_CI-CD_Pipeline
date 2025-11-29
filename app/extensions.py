from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from sqlalchemy.orm import DeclarativeBase

# Base class for ALL MODELS — stored here to avoid circular imports
class Base(DeclarativeBase):
    pass

# SQLAlchemy uses OUR Base
db = SQLAlchemy(model_class=Base)

ma = Marshmallow()
limiter = Limiter(key_func=get_remote_address, default_limits=[])
cache = Cache()
