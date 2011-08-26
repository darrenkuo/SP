#!/usr/bin/python

from os import mkdir
from os.path import exists

def setup_dbs():
    """
    (conn, cursor) = getDbCursor(course_db)
    cursor.execute('CREATE TABLE chapter(id INTEGER PRIMARY KEY, path TEXT);')
    conn.commit()
    cursor.close()
    """

    if not exists('dbs/admin_login.db'):
        (conn, cursor) = getDbCursor('dbs/admin_login.db')
        cursor.execute('CREATE TABLE users (login TEXT primary key, salt TEXT, saltpw TEXT);')
        conn.commit()
        cursor.close()

def setup(directory):
    print "Creating database folder"
    try:
        mkdir('dbs')
    except:
        pass
    setup_dbs()

    try:
        mkdir('dbs/student_database')
    except:
        pass    
        
    if not exists('requests'):
        mkdir('requests')
        mkdir('requests/quiz')
        mkdir('requests/admin')

if __name__ == '__main__':

    if len(argv) != 2:
        print "Usage: python setup.py <setup directory>"
    else:
        setup_dir = argv[1]
        setup(setup_dir)
