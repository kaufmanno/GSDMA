
.. code:: ipython3

    import sqlite3

.. code:: ipython3

    conn = sqlite3.connect('E_F10.db')

.. code:: ipython3

    c = conn.cursor()

.. code:: ipython3

    def create_table(cursor, name, fields):
        cmd = "CREATE TABLE IF NOT EXISTS {table_name}(".format(table_name=name)
        for k, v in fields.items():
            cmd = cmd + '{field} {field_type}, '.format(field=k, field_type=v)
        cmd = cmd[:-2]+')'
        print(cmd)
        cursor.execute(cmd)

.. code:: ipython3

    table_names = ['Boreholes', 'Intervals']
    fields = [{'name': 'TEXT'},{'borehole': 'TEXT', 'start': 'REAL', 'end': 'REAL', 'description': 'TEXT'}]
    for i in range(len(table_names)):
        create_table(c, table_names[i], fields[i])


.. parsed-literal::

    CREATE TABLE IF NOT EXISTS Boreholes(name TEXT)
    CREATE TABLE IF NOT EXISTS Intervals(borehole TEXT, start REAL, end REAL, description TEXT)


.. code:: ipython3

    conn.commit()


.. code:: ipython3

    c.close ()

.. code:: ipython3

    conn.close()


