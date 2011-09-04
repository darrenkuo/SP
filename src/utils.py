from os import remove
from os.path import exists
from os.path import join
from shutil import copyfile
from subprocess import Popen, PIPE
from sqlite3 import connect
from time import strftime, localtime, time

from globals import *

def getDbCursor(db):
    db_conn = connect(join(dbs_path, db))
    db_cursor = db_conn.cursor()
    return (db_conn, db_cursor)

def newLessonData(index, title, code, page_type):
    return {'index' : index, 'chapters' : [],
            'title' : title, 'readable' : code,
            'type' : page_type}

def readLessonData(path):
    f = open(join(course_material, path, 'lesson.data'), 'r')
    data = eval(f.read())
    f.close()

    return data

def writeLessonData(path, data):
    f = open(join(course_material, path, 'lesson.data'), 'w')
    f.write(str(data))
    f.close()

def checkReadable(lesson_data, user):
    func = eval('lambda time, user: %s' % (lesson_data['readable']))
    return func(time() * 1000, user)

def checkAccessed(index, user, oldconn=None, oldcursor=None):
    if not oldconn or not oldcursor:
        #(conn, cursor) = getDbCursor(course_db)
        (conn, cursor) = getDbCursor(getUserDb(user))
    else:
        conn = oldconn
        cursor = oldcursor

    cursor.execute('SELECT * from visits v where v.login = "%s" and v.chapter_id = "%s"' % (user, str(index)))

    rows = cursor.fetchall()

    if not oldconn:
        cursor.close()
    
    return len(rows) == 1

def getUserDb(user):
    db_file = join('student_database', user + '.db')
    if exists(join('dbs',db_file)):
        #print "user file exists", user
        return db_file

    print exists(db_file), db_file

    from web.utils import sendmail
    sendmail('cs61as@imail.eecs.berkeley.edu', 
             'cs61as-tb@imail.eecs.berkeley.edu',
             'New student: %s' % (user),
             '%s has join cs61as' % (user))
    
    (conn, cursor) = getDbCursor(db_file)
    cursor.execute('CREATE TABLE visits_times(login TEXT, chapter_id INTEGER, timestamp INTEGER);')
    cursor.execute('CREATE TABLE quiz_times(login TEXT, chapter_id INTEGER, timestamp INTEGER);')
    cursor.execute('CREATE TABLE visits(login TEXT, chapter_id INTEGER);')
    cursor.execute('CREATE TABLE SPECIAL_FLAG(login TEXT, SPECIAL_FLAG TEXT);')
    cursor.execute('CREATE TABLE solution_times(assignment TEXT, timestamp INTEGER);')
    conn.commit()
    cursor.close()
    return db_file

def checkSF(SF, user):
    #(conn, cursor) = getDbCursor(course_db)
    (conn, cursor) = getDbCursor(getUserDb(user))
    cursor.execute('SELECT * from SPECIAL_FLAG where login = "%s" and SPECIAL_FLAG = "%s";' % (user, SF))
    rows = cursor.fetchall()
    cursor.close()
    return len(rows) >= 1

def storeAssignmentTime(assignment, user):
    if not sawSolution(assignment, user):
        from web.utils import sendmail
        sendmail('cs61as@imail.eecs.berkeley.edu', 
                 'cs61as-tb@imail.eecs.berkeley.edu',
                 'Student: %s read solutions for %s' % (user, assignment),
                 'Student: %s read solutions for %s at %s' % (user, assignment, strftime("%Y/%m/%d %H:%M:%S", localtime())))

    (conn, cursor) = getDbCursor(getUserDb(user))
    print 'store', assignment, user
    conn.execute('insert into solution_times values("%s", %s);' % (assignment,
                                                                  str(int(time() * 1000))))
    conn.commit()
    cursor.close()

def sawSolution(assignment, user):
    (conn, cursor) = getDbCursor(getUserDb(user))
    cursor.execute('select * from solution_times where assignment="%s";' % (assignment))
    rows = cursor.fetchall()
    cursor.close()
    return len(rows) >= 1
    
def storeVisit(index, user):
    #(conn, cursor) = getDbCursor(course_db)
    (conn, cursor) = getDbCursor(getUserDb(user))
    if not checkAccessed(index, user, conn, cursor):
        #print "storing visit: %s just accessed page %s" % (user, index)
        cursor.execute('INSERT into visits values("%s", "%s");' % (user, str(index)))
        conn.commit()
    #else:
    #    print "%s have already accessed page %s before" % (user, index)

    cursor.execute('INSERT into visits_times values("%s", "%s", "%s");' % (user, str(index), str(int(time() * 1000))))
    conn.commit()
    cursor.close()    

def convertToRealPath(path):
    return apply(join, path.split('-'))

def isAdmin(user):
    (conn, cursor) = getDbCursor(admin_db)
    cursor.execute('SELECT * from users a WHERE a.login = "%s";' % (user))
    rows = cursor.fetchall()
    return len(rows) == 1

def isStudent(user):
    return exists(join(dbs_path, 'student_database', '%s.db' % (user)))

def setup_dbs():
    if not exists(join(dbs_path, course_db)):
        (conn, cursor) = getDbCursor(course_db)
        cursor.execute('CREATE TABLE chapter(id INTEGER PRIMARY KEY, path TEXT);')
        conn.commit()
        cursor.close()

    if not exists(join(dbs_path, admin_db)):
        (conn, cursor) = getDbCursor(admin_db)
        cursor.execute('CREATE TABLE users (login TEXT primary key);')
        conn.commit()
        cursor.close()

def clean_html(html):
    html = html.replace('\xc2', '.')
    html = html.replace('\xb1', '+-')
    html = html.replace('\xc3', ' ')
    html = html.replace('\x96', ' ')
    html = html.replace('\xbc', ' ')
    html = html.replace('\xce', ' ')
    html = html.replace('\xdb', ' ')
    html = html.replace('\xa3', ' ')
    html = html.replace('\xd9', ' ')
    html = html.replace('\xae', ' ')
    html = html.replace('\xb7', ' ')
    
    return html

def new_chapter(n):
    from course_admin import make_new_page

    newID = make_new_page({'title' : 'NONE', 'page':'.', 'code' : 'True', 'type' : 'lesson'})

    newID = str(newID)
    code = "True and checkAccessed(%s, user)" % newID

    id1 = make_new_page({'title' : 'Lecture Notes %d' % (n), 'page' : join('.', newID), 'code' : code, 'type' : 'lesson'})
    id1 = str(id1)
    remove(join(course_material, '.', newID, id1, 'content.html'))
    copyfile('/home/darren/Documents/61AS/tex/notes_out/%s.html' % (n), join(course_material, '.', newID, id1, 'content.html'))

    id1 = make_new_page({'title' : '(Optional) Lecture Webcast %d' %(n), 'page' : join('.', newID), 'code' : code, 'type' : 'lesson'})
    id1 = str(id1)
    
    content = open(join(course_material, '.', newID, id1, 'content.html'), 'w')
    content.write("""<ul> 
  <li>Lecture 1: functional programming 1</li> 
  <li>Lecture 2: functional programming 2</li> 
</ul> 
<a href="http://webcast.berkeley.edu/playlist#c,d,Computer_Science,3E89002AA9B9879E" target="_blank">Watch Lecture Video at webcast.berkeley.edu</a> """)
    content.close()

    id1 = make_new_page({'title' : 'Lab %d' % (n), 'page' : join('.', newID), 'code' : code, 'type' : 'lesson'})
    id1 = str(id1)
    remove(join(course_material, '.', newID, id1, 'content.html'))
    copyfile('/home/darren/Documents/61AS/tex/labs_out/%s.html' % (n), join(course_material, '.', newID, id1, 'content.html'))
    id1 = make_new_page({'title' : 'Homework %d' % (n), 'page' : join('.', newID), 'code' : code, 'type' : 'lesson'})
    id1 = str(id1)
    remove(join(course_material, '.', newID, id1, 'content.html'))
    copyfile('/home/darren/Documents/61AS/tex/hws_out/%s.html' % (n), join(course_material, '.', newID, id1, 'content.html'))
    make_new_page({'title' : 'Reading for next week', 'page' : join('.', newID), 'code' : code, 'type' : 'lesson'})

def lastVisitedPage(user):
    (conn, cursor) = getDbCursor(course_db)
    cursor.execute("SELECT * from visits_times;")
    rows = cursor.fetchall()

    max_row = (None, None, 0)    
    for r in rows:
        if r[-1] > max_row[-1]:
            max_row = r
        
    cursor.execute('SELECT * from chapter where ID=%s;' % (max_row[1]))
    page = cursor.fetchall()[0]

    conn.close()
    
    return str(page[1])

def regenerateNext(root='.'):
    from utils import readLessonData
    stack = []
    data = readLessonData(root)
    stack.extend(data['chapters'])

    done = []

    while len(stack) != 0:
        c = stack[0]
        done.append(c)
        stack = stack[1:]
        data = readLessonData(getRealPath(c))
        d = list(data['chapters'])
        d.extend(stack)
        stack = d
    
    done = map(str, done)
    f = open('static/course_flow', 'w')
    f.write(str(done))
    f.close()

def getRealPath(lesson_number):
    (conn, cursor) = getDbCursor('course.db')
    cursor.execute('select tmp.path from chapter tmp where tmp.id=%s;'% (lesson_number))
    rows = cursor.fetchall()
    return str(rows[0][0])

def findPreviousNext(path, user):
    f = open('static/course_flow', 'r')
    flow = eval(f.read())
    f.close()

    p = path.split('-')[-1]

    start = -1
    for i in range(len(flow)):
        if flow[i] == p:
            start = i + 1
            break

    if start == -1:
        return '/magic?page=/summary'

    
    while True and start < len(flow):
        real_path = getRealPath(flow[start])
        data = readLessonData(real_path)
        html_path = '-'.join(real_path.split("/")[1:])
        if checkReadable(data, user):
            return '/magic?page=/display?page=%s' % (html_path)

        start += 1

    return '/magic?page=/summary'
                
def getGrades(user):
    proc = Popen(['glookup', user], stdout=PIPE, stderr=PIPE)
    (o, e) = proc.communicate()

    if e:
        return "ERROR:" + e
    else:
        o = o.split('\n')
        output = o[0]
        categories = o[1].replace('-', ' ').split()
        total = o[-1]
        o = o[2:-1]

        output += '<table border="0">'
        output += '<tr>'
        for c in categories:
            output += '<td><center>%s</center></td>' % (c)
        output += '</tr>'

        for i in o:
            tmp = i.split()
            output += '<tr>'
            for j in tmp:
                output += '<td><center>%s</center></td>' % (j)
            output += '</tr>'

        output += '</table>'                
        
        return output

    
