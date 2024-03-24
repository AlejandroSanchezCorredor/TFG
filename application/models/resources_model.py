from application.core.sql import db, BaseModel


class ResourcesCategories(BaseModel):
    __tablename__ = 'categories'

    name = db.Column(db.String(100))
    code = db.Column(db.String(100))