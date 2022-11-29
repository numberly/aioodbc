import asyncio
import gc
import os
import uuid
from concurrent.futures import ThreadPoolExecutor

import aioodbc
import pytest
import pytest_asyncio
import uvloop


@pytest.fixture(scope='session')
def session_id():
    """Unique session identifier, random string."""
    return str(uuid.uuid4())


def pytest_generate_tests(metafunc):
    if 'loop_type' in metafunc.fixturenames:
        loop_type = ['default', 'uvloop']
        metafunc.parametrize("loop_type", loop_type, scope='session')


@pytest.fixture(scope='session')
def event_loop(loop_type):
    if loop_type == 'default':
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    elif loop_type == 'uvloop':
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop_policy().new_event_loop()

    try:
        yield loop
    finally:
        gc.collect()
        loop.close()


# alias
@pytest.fixture(scope='session')
def loop(event_loop):
    return event_loop


@pytest.fixture
def executor():
    executor = ThreadPoolExecutor(max_workers=1)

    try:
        yield executor
    finally:
        executor.shutdown(True)


def pytest_configure():
    pytest.db_list = ['pg', 'mysql', 'sqlite']


@pytest.fixture
def db(request):
    return 'sqlite'


@pytest.fixture
def dsn(tmp_path, request, db):
    if db == 'pg':
        return "Driver=PostgreSQL Unicode;Server=postgres;Port=5432;Database=postgres;Uid=postgres;Pwd=postgres;"  # noqa
    elif db == 'mysql':
        return "Driver=MySQL ODBC 8.0 Driver;Server=mysql;Port=3306;Database=mysql;User=root;Password=mysql"  # noqa
    elif db == 'sqlite':
        return os.environ.get('DSN', f'Driver=SQLite3;Database={tmp_path / "sqlite.db"}')  # noqa


@pytest_asyncio.fixture
async def conn(loop, dsn, connection_maker):
    connection = await connection_maker()
    return connection


@pytest_asyncio.fixture
async def connection_maker(loop, dsn):
    cleanup = []

    async def make(**kw):
        if kw.get('executor', None) is None:
            executor = ThreadPoolExecutor(max_workers=1)
            kw['executor'] = executor
        else:
            executor = kw['executor']
        conn = await aioodbc.connect(dsn=dsn, loop=loop, **kw)
        cleanup.append((conn, executor))
        return conn

    try:
        yield make
    finally:
        for conn, executor in cleanup:
            await conn.close()
            executor.shutdown(True)


@pytest_asyncio.fixture
async def pool(loop, dsn):
    pool = await aioodbc.create_pool(loop=loop, dsn=dsn)

    try:
        yield pool
    finally:
        pool.close()
        await pool.wait_closed()


@pytest_asyncio.fixture
async def pool_maker(loop):
    pool_list = []

    async def make(loop, **kw):
        pool = await aioodbc.create_pool(loop=loop, **kw)
        pool_list.append(pool)
        return pool

    try:
        yield make
    finally:
        for pool in pool_list:
            pool.close()
            await pool.wait_closed()


@pytest_asyncio.fixture
async def table(loop, conn):

    cur = await conn.cursor()
    await cur.execute("CREATE TABLE t1(n INT, v VARCHAR(10));")
    await cur.execute("INSERT INTO t1 VALUES (1, '123.45');")
    await cur.execute("INSERT INTO t1 VALUES (2, 'foo');")
    await conn.commit()
    await cur.close()

    try:
        yield 't1'
    finally:
        cur = await conn.cursor()
        await cur.execute("DROP TABLE t1;")
        await cur.commit()
        await cur.close()
