from application.core.sql.defaults.sql_context import SQLContext
from application.functions.db.database_workspace import reduce_permissions


@SQLContext()
def get_user_permissions(email=None, update_access=False, _session_=None):
    from application.models.users_model import Users

    user = _session_.query(Users).filter_by(email=email).first()

    return user.id
    #return user.id, reduce_permissions(user)
