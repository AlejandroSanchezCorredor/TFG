from application.core.sql.sql_session import db_get_session

# [INFO] For external sql context logic (init + audit)

class SQLContext(object):
    def __call__(self, orig_func):
        def wrapper(*args, **kwargs):
            session = db_get_session()
            try:
                kwargs['_session_'] = session
                res = orig_func(*args, **kwargs)
                session.commit()
                return res
            except Exception as e:
                print("[SQL CONTEXT] Error", e)
            finally:
                session.close()

        return wrapper

