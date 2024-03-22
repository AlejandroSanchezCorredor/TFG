from application.core.sql import db, BaseModel


class Chats(BaseModel):
    __tablename__ = 'chat'

    id = db.Column(db.String(100), nullable=False, primary_key=True, unique=True)
    id_book = db.Column(db.String(100), db.ForeignKey('book.id'), nullable=False)
    content = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    sender = db.Column(db.String(100), nullable=False)
    receiver = db.Column(db.String(100), nullable=False)

