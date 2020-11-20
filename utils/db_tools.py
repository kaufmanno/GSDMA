import sqlite3
import pandas as pd
import pyvista as pv


def db_copy_sqlite3_tables(db_in, db_out, tables):
    """
    Copy tables from one database to another
    :param db_in: full filename of the origin of tables 
    :type db_in: string
    :param db_out: full filename of the destination of tables
    :type db_in: string
    :param tables: list of tables to copy
    :type tables: list
    :return: status, 0: OK, 1: failure
    :rtype: int
    :param name: name of the table
    """
    
    status = 0
    try:
        conn_in = sqlite3.connect(db_in)
        conn_out = sqlite3.connect(db_out)
        for i in tables:
            df = pd.read_sql_query("SELECT * from {table:s}".format(table=i), conn_in)
            df.to_sql("{table:s}".format(table=i),conn_out, if_exists='replace', index = False)
        conn_in.close()
        conn_out.close()
    except Exception as e:
        print('Error copying tables:\n {error:s}'.format(error=e))
        status = 1
    return status
            

def create_table(conn, name, fields, commit=True, verbose=False):
    """ Creates a table if it does not exist and add fields
    
    :param conn: a connection to a SQLITE3 database
    :type conn: sqlite3.Connection
    :param name: name of the table
    :type name: string
    :param fields: a dict of fields and types of the table
    :type fields: dict
    :param commit: if True, commits changes to the database before exiting
    :type commit: boolean
    :param verbose: if True, displays the SQL command before execution
    :type verbose: boolean
    :return: status, 0: OK, 1: failure
    :rtype: int
    """
    
    status = 0
    try:
        cursor=conn.cursor()
        cmd = "CREATE TABLE IF NOT EXISTS {table_name}(".format(table_name=name)
        for k, v in fields.items():
            cmd = cmd + '{field} {field_type}, '.format(field=k, field_type=v)
        cmd = cmd[:-2]+')'
        if verbose:
            print(cmd)
        cursor.execute(cmd)
        if commit:
            conn.commit()
    except Exception as e:
        print('Error while creating table {table:s}: \n{error:s}'.format(table=name, error=e))
        status = 1
    return status


def boreholes_dict_to_sqlite3_db(boreholes, conn, commit=True, verbose=False):
    """ Stores data from a boreholes dict into a SQLITE3 database
    
    :param boreholes: boreholes
    :type boreholes: dict
    :param conn: a connection to a SQLITE3 database
    :type conn: sqlite3.Connection
    :param commit: if True, commits changes to the database before exiting
    :type commit: boolean
    :param verbose: if True, displays the SQL command before execution
    :type verbose: boolean
    :return: status, 0: OK, 1: failure
    :rtype: int
    """

    status = 0
    try:
        c = conn.cursor()
        # create new tables
        table_names = ['Boreholes', 'Intervals','Components','Lexicon']
        fields = [{'id': 'TEXT'},{'borehole': 'TEXT', 'top': 'REAL', 'base': 'REAL', 'description': 'TEXT'},{'borehole':'TEXT','top': 'REAL', 'base': 'REAL', 'key':'TEXT','value':'TEXT'},{'key':'TEXT', 'value':'TEXT'}]
        for i in range(len(table_names)):
            create_table(conn, table_names[i], fields[i], commit=False, verbose=verbose)
        
        # Insert values into Boreholes, Intervals and Components tables
        for k, v in boreholes.items():
            sql_command = "INSERT INTO Boreholes (id) VALUES ('{id}')".format(id=k)
            c.execute(sql_command)
            for k2,v2 in v.items():
                if k2 not in ('markers',):
                    sql_command = "INSERT INTO Intervals VALUES ('{id}', {top:.2f}, {base:.2f}, '{description:s}')".format(id=k, top=k2[0], base=k2[1], description=v2['description'])
                    if verbose:
                        print(sql_command)
                    c.execute(sql_command)       
        for k, v in boreholes.items():
            for k2,v2 in v.items():
                if k2 not in ('markers',):
                    for k3, v3 in v2.items():
                        if k3 not in ('description',):
                            sql_command = "INSERT INTO Components VALUES ('{id}', {top:.2f}, {base:.2f}, '{key:s}', '{value:s}')".format(id=k, top=k2[0], base=k2[1], key=k3, value=v3)
                            if verbose:
                                print(sql_command)
                            c.execute(sql_command)
                            
        # Build a Lexicon from borehole data
        temp = {'colour': [], 'lithology': []}
        for bh_name, bh_ in boreholes.items():
            for k2,v2 in bh_.items():
                if k2 not in ('markers',):
                    for k3, v3 in v2.items():
                        if k3 in ('lithology', 'colour'):
                            temp[k3].append(v3)
        Lexicon={}
        Lexicon['colour'] = list(set(temp['colour']))
        Lexicon['lithology'] = list(set(temp['lithology']))
       
        for k,v in Lexicon.items():
            for i in v:
                sql_command = "INSERT INTO Lexicon VALUES ('{key:s}', '{value:s}')".format(key=k, value=i)
                if verbose:
                    print(sql_command)
                c.execute(sql_command)
        if commit:
            conn.commit()
    
    except Exception as e:
        print('Error while creating tables: {error:s}'.format(error=e))
        status = 1
    
    return status

def add_interval_list(intervals,plotter,radius=.09):
    """
    add a list of intervals to a plotter 
    :param intervals: list of intervals to add to the plotter 
    :type intervals: list
    :param plotter: plotter pyvista 
    :type plotter: pyvista.plotting.plotting.Plotter
    :param radius: radius of the boreholes (if different radii, make distinct lists of intervals)
    :type radius: float
    """    
    cylinders = []
    i = 0
    for interval in intervals:
        
        i = intervals.index(interval)
        
        center = (interval.base.middle - interval.top.middle)/2
        height = interval.base.middle - interval.top.middle
        
        cylinders.append( 
                    pv.Cylinder(
                                    center = center,
                                    height = height,
                                    direction = (0.0, 0.0, 1.0),
                                    radius = radius, 
                                    
                                  )
                        
                            )
    
        plotter.add_mesh(cylinders[i], color="tan", show_edges=False)
    print(2)
    print(type(plotter))
    print(type(radius))
    plotter.show(auto_close=False, use_panel=True)
