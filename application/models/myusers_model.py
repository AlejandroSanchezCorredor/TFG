from application.core.sql import db, BaseModel


class Users(BaseModel):
    __tablename__ = 'user'

    id = db.Column(db.String(100), nullable=False, primary_key=True, unique=True)
    email = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.Integer)
    address = db.Column(db.String(100))
    nationality = db.Column(db.String(100))