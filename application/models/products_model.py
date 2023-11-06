from application.core.sql import db, BaseModel


class Products(BaseModel):
    __tablename__ = 'products'

    name = db.Column(db.String(100))
    code = db.Column(db.String(100))