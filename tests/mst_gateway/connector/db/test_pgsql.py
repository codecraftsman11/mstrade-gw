# pylint: disable=no-self-use,invalid-name,redefined-outer-name,no-member,broad-except
import io
import pytest
from nc_amqp_worker.connector import db
from nc_amqp_worker.auth import login
from nc_amqp_worker.exceptions import QueryError
from tests.config import POSTGRESQL_CONNECT_CFG, POSTGRESQL_LOGIN_AUTH_CFG

DB_SCHEMA_FILE = "tests/files/schema/pgsql/db.sql"


@pytest.fixture
def auth():
    return login.Auth(POSTGRESQL_LOGIN_AUTH_CFG)


@pytest.fixture
def _pgsql0(auth):
    with db.connect(params=POSTGRESQL_CONNECT_CFG, auth=auth) as _con:
        _con.autocommit = True
        cursor = _con.cursor()
        cursor.execute("DROP DATABASE IF EXISTS test;")
        cursor.execute("CREATE DATABASE test;")
        yield _con


@pytest.fixture
def connect(auth, _pgsql0):
    test_db_config = POSTGRESQL_CONNECT_CFG.copy()
    test_db_config['dbname'] = 'test'
    with db.connect(params=test_db_config, auth=auth) as db_conn:
        sql_buff = ""
        with io.open(DB_SCHEMA_FILE) as schema_file:
            for line in schema_file:
                sql_buff += line
        cursor = db_conn.cursor()
        cursor.execute(sql_buff)
        cursor.close()
        yield db_conn


class TestPostgreSQL(object):
    def test_connector(self, connect):
        assert connect

    def test_insert(self, connect):
        try:
            _insert_records(connect)
            assert True
        except Exception:
            assert False

    def test_select(self, connect):
        _insert_records(connect)
        cur = connect.cursor()
        cur.execute("SELECT "
                    "email,forwardedto "
                    "FROM email_forwarding "
                    "WHERE "
                    "email=%s;", ['test123@example.com'])
        row = cur.fetchone()
        cur.close()
        assert row == ('test123@example.com', 'belka158@gmail.com')

    def test_select_unbuf(self, connect):
        _insert_records(connect)
        cur = connect.cursor(buffered=False)
        cur.execute("SELECT "
                    "email,forwardedto "
                    "FROM email_forwarding "
                    "WHERE "
                    "email=%s;", ['test123@example.com'])
        row = cur.fetchone()
        cur.close()
        assert row == ('test123@example.com', 'belka158@gmail.com')

    def test_pgsql_closed_connection(self, connect, _pgsql0):
        cur = connect.cursor()
        cur.execute("select pg_backend_pid()")
        connection_id = cur.fetchone()[0]
        with pytest.raises(QueryError):
            cur.execute("SELECT 1 FROM non_existing_table WHERE 0")
        _pgsql0.cursor().execute("select pg_terminate_backend(%s)", (connection_id,))
        assert connect.cursor()
        with pytest.raises(Exception):
            try:
                cur.execute("SELECT 1 FROM email_domains WHERE 0")
            except QueryError:
                pass
        with pytest.raises(Exception):
            connect.rollback()
        with pytest.raises(Exception):
            connect.commit()


def _insert_records(_pgsql):
    cur = _pgsql.cursor()
    cur.execute("INSERT INTO "
                "email_domains ("
                "domainId,"
                "domainName"
                ") VALUES "
                "(%s, %s)", [1, 'example.com'])
    cur.execute("INSERT INTO "
                "email_forwarding ("
                "email,"
                "forwardedTo,"
                "domainId"
                ") VALUES "
                "(%s, %s, %s);",
                ['test123@example.com', 'belka158@gmail.com', 1])
    _pgsql.commit()
