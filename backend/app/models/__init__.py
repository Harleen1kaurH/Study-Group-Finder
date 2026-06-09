# Import all models here so Alembic can detect them when generating migrations
from app.models.user import User
from app.models.course import Course
from app.models.group import Group, GroupMember
from app.models.session import Session, SessionSlot, SlotVote, SessionStatus
from app.models.notification import Notification
