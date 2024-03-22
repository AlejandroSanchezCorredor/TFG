from application.core.sql import db, BaseModel


class Users(BaseModel):
    __tablename__ = 'users'

    email = db.Column(db.String(100), nullable=False, unique=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)


