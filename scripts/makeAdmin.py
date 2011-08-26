from os.path import join
from sqlite3 import connect
from sys import argv

def getDbCursor(db):
    db_conn = connect(db)
    db_cursor = db_conn.cursor()
    return (db_conn, db_cursor)

def makeAdmin(db_file, admin_request):
    f = open(admin_request, 'r')
    info = f.read().strip().split('\n')
    f.close()

    (conn, cursor) = getDbCursor(db_file)
    cursor.execute('INSERT into users values("%s", "%s", "%s");' % 
                   tuple(info))

    conn.commit()
    cursor.close()

if __name__ == '__main__':
    if len(argv) != 3:
        print "Usage: python makeAdmin.py <database-file> <request-file>"
    else:
        makeAdmin(argv[1], argv[2])
