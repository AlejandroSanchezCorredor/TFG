from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from ..configuration_loader import get_configuration

def db_get_session(db_name=None):

    def create_sessionmaker():
        config = get_configuration()
        engine = create_engine(db_get_conn_string(db_name), echo=config.DEBUG_SQL,
                               pool_size=20, pool_recycle=3600, max_overflow=0)

        return sessionmaker(bind=engine)

    _session = create_sessionmaker()
    return _session()


def db_get_conn_string(db_name):
    config = get_configuration()

    driver = config.DATABASE_TYPE
    port = config.DATABASE_PORT
    host = config.DATABASE_URI
    username = config.DATABASE_USER
    password = config.DATABASE_PASSWORD
    dbname = db_name or config.DATABASE_DB
    dboptions = 'charset=utf8mb4'

    conn_string = '{}://{}:{}@{}:{}/{}?{}'.format(driver, username, password, host, port, dbname, dboptions)

    return conn_string
