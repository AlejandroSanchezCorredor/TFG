from application.core.configuration_loader import get_configuration
from application.core.sql.sql_session import db_get_session


def create_database(db_name):
    config = get_configuration()
    session = db_get_session()

    _db_name = None
    _db_version = None

    if db_name:
        _db_name = f'{config.DATABASE_SUSCRIPTOR_PREFIX}{db_name}'

        existing_databases = session.execute("SHOW DATABASES")
        existing_databases = [ed[0] for ed in existing_databases]

        print(f'[STEP 0] Checking exist database [{_db_name}]')
        if _db_name not in existing_databases:
            print(f'[STEP 1] Creating database [{_db_name}]')
            session.execute("CREATE DATABASE IF NOT EXISTS {0} ".format(_db_name))
        else:
            print(f'> Database [{_db_name}] already exist')

    session.close()

    print(f'[STEP 2] Cloning schema from [{config.DATABASE_BASE_DB}] into [{_db_name}]')
    _db_version = clone_database_base(_db_name)

    print(f'[STEP 3] Inserting static data into [{_db_name}]')
    insert_database_static_data(db_name=_db_name, db_version=_db_version)

    return _db_name, _db_version


def delete_database(db_name):
    config = get_configuration()
    session = db_get_session()

    if db_name:
        # _db_name = f'{config.DATABASE_SUSCRIPTOR_PREFIX}{db_name}'

        existing_databases = session.execute("SHOW DATABASES")
        existing_databases = [ed[0] for ed in existing_databases]

        print(f'[STEP 0] Checking exist database [{db_name}]')
        if db_name in existing_databases:
            print(f'[STEP 1] Deleting database [{db_name}]')
            session.execute("DROP DATABASE IF EXISTS {0} ".format(db_name))
        else:
            print(f'> Database [{db_name}] not exist')

    session.close()
    return db_name


def clone_database_base(db_name):
    from application.core.sql import db, Base, BaseModel

    session = db_get_session(db_name=db_name)

    # Check and include 'alembic_version' metadata model if not exist (for creation)
    alembic_version = next((t for t in Base.metadata.sorted_tables if t.name == 'alembic_version'), None)
    if alembic_version is None:
        alembic_version = db.Table(
            'alembic_version', Base.metadata,
            db.Column("version_num", db.String(32), nullable=False)
        )

    _db_base_version = BaseModel.session.query(alembic_version).first()
    Base.metadata.create_all(session.get_bind())

    return _db_base_version.version_num


def get_suscriptors_databases():
    config = get_configuration()
    session = db_get_session()

    existing_databases = session.execute("SHOW DATABASES")
    suscriptors_databases = [ed[0] for ed in existing_databases if config.DATABASE_SUSCRIPTOR_PREFIX in ed[0]]

    return suscriptors_databases


def alembic_upgrade_database(db_name=None):
    import os, argparse
    from alembic import command, config

    # INFO: db_name = '<database_name>' > specific database / db_name = 'multiple' > All suscriptors databases

    # Recover default base configuration
    config = config.Config(f'{os.path.abspath(os.curdir)}/alembic.ini', ini_section='alembic_base')

    # Set argument (simulate command)
    config.cmd_opts = argparse.Namespace()
    setattr(config.cmd_opts, 'x', [f'database={db_name}'])

    # Execute upgrade command
    command.upgrade(config, "head")

    # TODO: Update Core Suscriptors Databases info!


def insert_database_static_data(db_name, db_version):
    from application.functions.db.init_database_base import insert_db_version, insert_permissions, insert_modules, insert_roles

    insert_db_version(__db_name__=db_name, __db_version__=db_version)

    # TIP: Order is important (dependency between entities)
    insert_permissions(__db_name__=db_name)
    insert_modules(__db_name__=db_name)
    insert_roles(__db_name__=db_name)
