import uuid
from application.core.sql import db, Base, BaseModel
from sqlalchemy.orm import relationship


class Users(BaseModel):
    __tablename__ = 'users'

    email = db.Column(db.String(100), nullable=False, unique=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)


