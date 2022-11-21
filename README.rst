aioodbc
=======
.. image:: https://github.com/numberly/aioodbc/workflows/test/badge.svg?branch=master
    :target: https://github.com/numberly/aioodbc/actions


**aioodbc** is a Python 3.8+ module that makes it possible to access ODBC_ databases
with asyncio_. It relies on the awesome pyodbc_ library and preserves the same look and
feel. Internally *aioodbc* employs threads to avoid blocking the event loop, threads_
are not that as bad as you think!. Other drivers like motor_ use the same approach.

**aioodbc** is fully compatible and tested with uvloop_. Take a look at the test
suite, all tests are executed with both the default event loop and uvloop_.

Supported Databases
-------------------

**aioodbc** should work with all databases supported by pyodbc_. But for now the
library has been tested with: **SQLite**, **MySQL** and **PostgreSQL**. Feel
free to add other databases to the test suite by submitting a PR.


Community
---------
Mailing List: https://groups.google.com/forum/#!forum/aio-libs

Chat room: https://gitter.im/aio-libs/Lobby


Basic Example
-------------

**aioodbc** is based on pyodbc_ and provides the same api, you just need
to use  ``yield from conn.f()`` or ``await conn.f()`` instead of ``conn.f()``

Properties are unchanged, so ``conn.prop`` is correct as well as
``conn.prop = val``.


.. code:: python

    import asyncio
    import aioodbc


    loop = asyncio.get_event_loop()


    async def test_example():
        dsn = 'Driver=SQLite3;Database=sqlite.db'
        conn = await aioodbc.connect(dsn=dsn, loop=loop)

        cur = await conn.cursor()
        await cur.execute("SELECT 42 AS age;")
        rows = await cur.fetchall()
        print(rows)
        print(rows[0])
        print(rows[0].age)
        await cur.close()
        await conn.close()

    loop.run_until_complete(test_example())


Connection Pool
---------------
Connection pooling is ported from aiopg_ and relies on PEP492_ features:

.. code:: python

    import asyncio
    import aioodbc


    loop = asyncio.get_event_loop()


    async def test_pool():
        dsn = 'Driver=SQLite3;Database=sqlite.db'
        pool = await aioodbc.create_pool(dsn=dsn, loop=loop)

        async with pool.acquire() as conn:
            cur = await conn.cursor()
            await cur.execute("SELECT 42;")
            r = await cur.fetchall()
            print(r)
            await cur.close()
            await conn.close()
        pool.close()
        await pool.wait_closed()

    loop.run_until_complete(test_pool())


Context Managers
----------------
`Pool`, `Connection` and `Cursor` objects support the context management
protocol:

.. code:: python

    import asyncio
    import aioodbc


    loop = asyncio.get_event_loop()


    async def test_example():
        dsn = 'Driver=SQLite3;Database=sqlite.db'

        async with aioodbc.create_pool(dsn=dsn, loop=loop) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute('SELECT 42 AS age;')
                    val = await cur.fetchone()
                    print(val)
                    print(val.age)

    loop.run_until_complete(test_example())


Installation
------------

In a linux environment pyodbc_ (hence *aioodbc*) requires the unixODBC_ library.
You can install it using your package manager, for example::

      $ sudo apt-get install unixodbc
      $ sudo apt-get install unixodbc-dev

then::

   pip install aioodbc


Run tests
---------

For testing purposes you need to install docker_

    $ make test

The test will automatically build container with
the required databases.

Other SQL Drivers
-----------------

* aiopg_ - asyncio client for PostgreSQL
* aiomysql_ - asyncio client form MySQL


Requirements
------------

* Python_ 3.8+
* pyodbc_
* uvloop_ (optional)


.. _Python: https://www.python.org
.. _asyncio: http://docs.python.org/3.4/library/asyncio.html
.. _pyodbc: https://github.com/mkleehammer/pyodbc
.. _uvloop: https://github.com/MagicStack/uvloop
.. _ODBC: https://en.wikipedia.org/wiki/Open_Database_Connectivity
.. _aiopg: https://github.com/aio-libs/aiopg
.. _aiomysql: https://github.com/aio-libs/aiomysql
.. _PEP492: https://www.python.org/dev/peps/pep-0492/
.. _unixODBC: http://www.unixodbc.org/
.. _threads: http://techspot.zzzeek.org/2015/02/15/asynchronous-python-and-databases/
.. _docker: https://docs.docker.com/engine/installation/
.. _motor: https://emptysqua.re/blog/motor-0-7-beta/
