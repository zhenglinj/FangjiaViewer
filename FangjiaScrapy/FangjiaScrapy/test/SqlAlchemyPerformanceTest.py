import time
import sqlite3

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

Base = declarative_base()
engine = None
DBSession = None
session = None


class Customer(Base):
    __tablename__ = "customer"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))


def init_sqlalchemy(dbname='sqlite:///sqlalchemy.db', refresh=True):
    global engine, DBSession, session
    engine = create_engine(dbname, echo=False)
    DBSession = scoped_session(sessionmaker())
    DBSession.remove()
    DBSession.configure(bind=engine, autoflush=False, expire_on_commit=False)
    if refresh:
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
    session = DBSession()


def test_sqlalchemy_orm(n=100000):
    init_sqlalchemy()
    t0 = time.time()
    for i in range(n):
        customer = Customer()
        customer.name = 'NAME ' + str(i)
        session.add(customer)
        if i % 1000 == 0:
            session.flush()
    session.commit()
    print(
        "SQLAlchemy ORM: Total time for " + str(n) +
        " records " + str(time.time() - t0) + " secs")


def test_sqlalchemy_orm_pk_given(n=100000):
    init_sqlalchemy()
    t0 = time.time()
    for i in range(n):
        customer = Customer(id=i + 1, name="NAME " + str(i))
        session.add(customer)
        if i % 1000 == 0:
            session.flush()
    session.commit()
    print(
        "SQLAlchemy ORM pk given: Total time for " + str(n) +
        " records " + str(time.time() - t0) + " secs")


def test_sqlalchemy_orm_bulk_save_objects(n=100000):
    init_sqlalchemy()
    t0 = time.time()
    n1 = n
    while n1 > 0:
        n1 = n1 - 10000
        session.bulk_save_objects(
            [
                Customer(name="NAME " + str(i))
                for i in range(min(10000, n1))
            ]
        )
    session.commit()
    print(
        "SQLAlchemy ORM bulk_save_objects(): Total time for " + str(n) +
        " records " + str(time.time() - t0) + " secs")


def test_sqlalchemy_orm_bulk_insert(n=100000):
    init_sqlalchemy()
    t0 = time.time()
    n1 = n
    while n1 > 0:
        session.bulk_insert_mappings(
            Customer,
            [
                dict(name="NAME " + str(i))
                for i in range(min(10000, n1))
            ]
        )
        n1 = n1 - 10000
    session.commit()
    print(
        "SQLAlchemy ORM bulk_insert_mappings(): Total time for " + str(n) +
        " records " + str(time.time() - t0) + " secs")


def test_sqlalchemy_core(n=100000):
    init_sqlalchemy()
    t0 = time.time()
    engine.execute(
        Customer.__table__.insert(),
        [{"name": 'NAME ' + str(i), "foo": "FOO"} for i in range(n)]
    )  ##==> engine.execute('insert into ttable (name) values ("NAME"), ("NAME2")')
    print(
        "SQLAlchemy Core: Total time for " + str(n) +
        " records " + str(time.time() - t0) + " secs")


def init_sqlite3(dbname, refresh=True):
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    if refresh:
        c.execute("DROP TABLE IF EXISTS customer")
        c.execute(
            "CREATE TABLE customer (id INTEGER NOT NULL, "
            "name VARCHAR(255), PRIMARY KEY(id))")
    conn.commit()
    return conn


def test_sqlite3(n=100000, dbname='sqlite3.db'):
    conn = init_sqlite3(dbname)
    c = conn.cursor()
    t0 = time.time()
    for i in range(n):
        row = ('NAME ' + str(i),)
        c.execute("INSERT INTO customer (name) VALUES (?)", row)
    conn.commit()
    print(
        "sqlite3: Total time for " + str(n) +
        " records " + str(time.time() - t0) + " sec")


def test_sqlalchemy_orm_query(n=100000):
    init_sqlalchemy(refresh=False)
    t0 = time.time()
    for i in range(n):
        customer = Customer()
        customer.name = 'NAME- ' + str(i)
        result_rows = session.query(Customer).filter(Customer.name == customer.name).first()
        if not result_rows:
            session.add(customer)
    session.commit()
    print(
        "SQLAlchemy ORM query: Total time for " + str(n) +
        " records " + str(time.time() - t0) + " secs")


def test_sqlite3_query(n=100000, dbname='sqlite3.db'):
    conn = init_sqlite3(dbname, refresh=False)
    c = conn.cursor()
    t0 = time.time()
    for i in range(n):
        row = ('NAME ' + str(i), )
        result_rows = c.execute("SELECT * FROM customer WHERE name=(?)", row).fetchall()
        if not result_rows:
            print("insert")
            c.execute("INSERT INTO customer (name) VALUES (?)", row)
    conn.commit()
    print(
        "sqlite3 query: Total time for " + str(n) +
        " records " + str(time.time() - t0) + " sec")


if __name__ == '__main__':
    # test_sqlalchemy_orm(100000)
    # test_sqlalchemy_orm_pk_given(100000)
    # test_sqlalchemy_orm_bulk_save_objects(100000)
    # test_sqlalchemy_orm_bulk_insert(100000)
    test_sqlalchemy_core(100000)
    # test_sqlite3(100000)
    # test_sqlalchemy_orm_query(100)
    # test_sqlite3_query(100)

# SQLAlchemy ORM: Total time for 100000 records 10.048169136047363 secs
# SQLAlchemy ORM pk given: Total time for 100000 records 6.3024210929870605 secs
# SQLAlchemy ORM bulk_save_objects(): Total time for 100000 records 2.406503200531006 secs
# SQLAlchemy ORM bulk_insert_mappings(): Total time for 100000 records 0.869683027267456 secs
# SQLAlchemy Core: Total time for 100000 records 0.4471921920776367 secs
# sqlite3: Total time for 100000 records 0.20742487907409668 sec

# SQLAlchemy ORM query: Total time for 100 records 0.06774210929870605 secs
# sqlite3 query: Total time for 100 records 0.7174410820007324 sec
