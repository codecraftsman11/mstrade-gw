# pylint: disable=no-self-use,invalid-name,redefined-outer-name,no-member,broad-except
import io
import pytest
from mst_gateway.connector import db
from mst_gateway.connector.db.mysql import MySQL
from mst_gateway.exceptions import QueryError
from mst_gateway.auth import login
from tests.config import MYSQL_CONNECT_CFG, MYSQL_LOGIN_AUTH_CFG

DB_SCHEMA_FILE = "tests/files/schema/mysql/db.sql"
TMP_TNAME = "test_mysql"


@pytest.fixture
def auth():
    return login.Auth(MYSQL_LOGIN_AUTH_CFG)


@pytest.fixture
def _mysql0(auth):
    test_db_config = MYSQL_CONNECT_CFG.copy()
    test_db_config['dbname'] = 'mysql'
    with db.connect(params=test_db_config, auth=auth, cls=MySQL) as _con:
        yield _con


@pytest.fixture
def _mysql1(auth):
    test_db_config = MYSQL_CONNECT_CFG.copy()
    test_db_config['dbname'] = 'mysql'
    with db.connect(params=test_db_config, auth=auth, cls=MySQL) as _con:
        yield _con


@pytest.fixture
def _mysql(_mysql0, auth):
    _mysql0.cursor().execute("DROP DATABASE IF EXISTS {dbname};"
                             "CREATE DATABASE {dbname};".format(**MYSQL_CONNECT_CFG),
                             multi=True)
    _mysql0.commit()

    with db.connect(params=MYSQL_CONNECT_CFG, auth=auth, cls=MySQL) as db_conn:
        sql_buff = ""
        with io.open(DB_SCHEMA_FILE) as schema_file:
            for line in schema_file:
                sql_buff += line
        db_conn.cursor().execute(sql_buff, multi=True)
        db_conn.commit()
        yield db_conn


class TestMySQL(object):
    def test_mysql_cursor_execute(self, _mysql0):
        print(_mysql0, _mysql0.handler)
        cursor = _mysql0.cursor()
        cursor.execute("DROP DATABASE IF EXISTS %s" % MYSQL_CONNECT_CFG['dbname'])
        cursor.execute("CREATE DATABASE %s" % MYSQL_CONNECT_CFG['dbname'])
        cursor.execute("SHOW DATABASES LIKE '%s'" % MYSQL_CONNECT_CFG['dbname'])
        row = cursor.fetchone()
        cursor.execute("DROP DATABASE IF EXISTS %s" % MYSQL_CONNECT_CFG['dbname'])
        cursor.close()
        _mysql0.commit()
        assert row == (MYSQL_CONNECT_CFG['dbname'],)

    def test_mysql_rollup(self, _mysql, _mysql0):
        cursor = _mysql.cursor()
        cursor.execute("INSERT INTO email_domains(domainname) VALUES ('test')")
        _mysql.rollback()
        cursor.execute("SELECT domainname FROM email_domains")
        assert cursor.fetchone() is None

    def test_mysql_for_update(self, _mysql, _mysql0):
        cursor = _mysql.cursor()
        cursor.execute("INSERT INTO email_domains(domainname) VALUES ('test')")
        _mysql.commit()
        cursor.execute("SELECT domainname FROM email_domains FOR UPDATE;")
        assert cursor.fetchone() == ('test',)

    def test_mysql_cursor_execute_multi(self, _mysql0):
        cursor = _mysql0.cursor()
        cursor.execute("DROP DATABASE IF EXISTS {dbname};"
                       "CREATE DATABASE {dbname};".format(**MYSQL_CONNECT_CFG),
                       multi=True)
        cursor.execute("SHOW DATABASES LIKE '%s'" % MYSQL_CONNECT_CFG['dbname'])
        row = cursor.fetchone()
        cursor.execute("DROP DATABASE IF EXISTS %s" % MYSQL_CONNECT_CFG['dbname'])
        cursor.close()
        _mysql0.commit()
        assert row == (MYSQL_CONNECT_CFG['dbname'],)

    def test_mysql_insert(self, _mysql):
        cur = _mysql.cursor()
        try:
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
            assert True
        except Exception:
            assert False

    def test_mysql_select(self, _mysql):
        cur = _mysql.cursor()
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
        cur.execute("SELECT "
                    "email,forwardedto "
                    "FROM email_forwarding "
                    "WHERE "
                    "email=%s;", ['test123@example.com'])
        row = cur.fetchone()
        cur.close()
        assert row == ('test123@example.com', 'belka158@gmail.com')

    def test_select_unbuf(self, _mysql):
        cur = _mysql.cursor(buffered=False)
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
        cur.execute("SELECT "
                    "email,forwardedto "
                    "FROM email_forwarding "
                    "WHERE "
                    "email=%s;", ['test123@example.com'])
        row = cur.fetchone()
        cur.close()
        assert row == ('test123@example.com', 'belka158@gmail.com')

    def test_mysql_closed_connection(self, _mysql, _mysql1):
        cur = _mysql.cursor()
        cur.execute("select connection_id()")
        connection_id = cur.fetchone()[0]
        with pytest.raises(QueryError):
            cur.execute("SELECT 1 FROM non_existing_table WHERE 0")
        _mysql1.cursor().execute("kill %s", (connection_id,))
        assert _mysql.cursor()
        with pytest.raises(Exception):
            try:
                cur.execute("SELECT 1 FROM email_domains WHERE 0")
            except QueryError:
                pass
        with pytest.raises(Exception):
            _mysql.rollback()
        with pytest.raises(Exception):
            _mysql.commit()
