from application.core.sql import db, BaseModel


class Flats(BaseModel):
    __tablename__ = 'flat'

    id = db.Column(db.String(100), nullable=False, primary_key=True, unique=True)
    id_user = db.Column(db.String(100), db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(100), nullable=False)