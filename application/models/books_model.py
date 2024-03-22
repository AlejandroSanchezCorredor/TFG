from application.core.sql import db, BaseModel


class Books(BaseModel):
    __tablename__ = 'book'

    id = db.Column(db.String(100), nullable=False, primary_key=True, unique=True)
    id_flat = db.Column(db.String(100), db.ForeignKey('flat.id'), nullable=False)
    checkin_date = db.Column(db.Date, nullable=False) # Date no incluye la hora, DateTime si
    checkout_date = db.Column(db.Date, nullable=False) 
    n_adults = db.Column(db.Integer, nullable=False)
    n_childrens = db.Column(db.Integer, nullable=False)
    n_rooms = db.Column(db.Integer, nullable=False)
    
