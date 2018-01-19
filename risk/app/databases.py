# -*- coding: utf-8 -*-

from contextlib import contextmanager

from sqlalchemy.orm.session import sessionmaker

Session = sessionmaker(autoflush=False)


@contextmanager
def session_scope(session=None):
    """Provide a transactional scope around a series of operations."""
    if not session:
        session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise

    try:
        session.close()
    except:
        session.remove()
