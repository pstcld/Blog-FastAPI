from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.orm import relationship
from .database import Base


class PublishedCreatedMixin:
    is_published = Column(Boolean, default=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    is_admin = Column(Boolean, default=False)

    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    likes = relationship("Like", back_populates="author", cascade="all, delete-orphan")


class Category(Base, PublishedCreatedMixin):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(256))
    description = Column(Text)
    slug = Column(String, unique=True, index=True)

    posts = relationship("Post", back_populates="category")


class Location(Base, PublishedCreatedMixin):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256))

    posts = relationship("Post", back_populates="location")


class Post(Base, PublishedCreatedMixin):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(256))
    text = Column(Text)
    pub_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    image = Column(String, nullable=True)

    author_id = Column(Integer, ForeignKey("users.id"))
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    author = relationship("User", back_populates="posts")
    location = relationship("Location", back_populates="posts")
    category = relationship("Category", back_populates="posts")
    comments = relationship(
        "Comment", back_populates="post", cascade="all, delete-orphan"
    )
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"))
    author_id = Column(Integer, ForeignKey("users.id"))

    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")
    likes = relationship("Like", back_populates="comment", cascade="all, delete-orphan")


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=True)
    comment_id = Column(
        Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True
    )

    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="uq_user_post_like"),
        UniqueConstraint("user_id", "comment_id", name="uq_user_comment_like"),
        CheckConstraint(
            "(post_id IS NOT NULL AND comment_id IS NULL) OR "
            "(post_id IS NULL AND comment_id IS NOT NULL)",
            name="chk_like_target",
        ),
    )

    author = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")
    comment = relationship("Comment", back_populates="likes")
