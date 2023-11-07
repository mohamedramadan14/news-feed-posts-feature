import databases
import sqlalchemy

from socialmedia.config import config

# Store info about tables , rows , cols
print(config)
metadata = sqlalchemy.MetaData()

# This args important for run sqlite in multithreading for background tasks as it's default nature is single threaded
# engine : allows us to connect to specific database like sqlite , mysql , postgres ..etc

connect_args = {"check_same_thread": False} if "sqlite" in config.DATABASE_URL else {}
engine = sqlalchemy.create_engine(config.DATABASE_URL, connect_args=connect_args)

post_table = sqlalchemy.Table(
    "posts",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("body", sqlalchemy.String),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id"), nullable=False),
    sqlalchemy.Column("image_url", sqlalchemy.String),
)

comment_table = sqlalchemy.Table(
    "comments",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("body", sqlalchemy.String),
    sqlalchemy.Column("post_id", sqlalchemy.ForeignKey("posts.id"), nullable=False),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id"), nullable=False),
)


user_table = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("email", sqlalchemy.String, unique=True),
    sqlalchemy.Column("password", sqlalchemy.String),
    sqlalchemy.Column("is_confirmed", sqlalchemy.Boolean, default=False),
)

like_table = sqlalchemy.Table(
    "likes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("post_id", sqlalchemy.ForeignKey("posts.id"), nullable=False),
    sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("users.id"), nullable=False),
)

# tell engine to use metadata to create all tables , and seed data if there is
metadata.create_all(engine)

# connect to database and give us back a database object to interact with database

db_args = {"minsize": 1, "maxsize": 3} if "postgres" in config.DATABASE_URL else {}
database = databases.Database(
    config.DATABASE_URL, force_rollback=config.DB_FORCE_ROLLBACK, **db_args
)
