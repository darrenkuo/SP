import src.web as web

from src.globals import *
from src.display import *
from src.lesson import *
from src.quiz import *
from src.summary import *
from src.course_admin import *
from src.utils import *
from src.solution import *

from os.path import exists
from subprocess import Popen, PIPE
from time import time

import sys

web.config.debug = True

urls = ('/', 'main', 
        '/logout', 'logout', 
        '/admin', 'admin',
        '/display', 'display',
        '/summary', 'summary', 
        '/lesson', 'lesson',
        '/lesson_page', 'lesson_page',
        '/lesson_nav', 'lesson_nav',
        '/magic', 'magic',
        '/grades', 'grades',
        '/quiz', 'quiz',
        '/course_admin', 'course_admin',
        '/course_control', 'course_control',
        '/edit_page', 'edit_page',
        '/new_page', 'new_page',
        '/up', 'up', 
        '/down', 'down',
        '/access', 'access',
        '/sidebar', 'sidebar',
        '/book', 'book',
        '/reader', 'reader',
        '/complain', 'complain',
        '/libraryfiles', 'libraryfiles',
        '/lecturefiles', 'lecturefiles',
        '/help', 'help',
        '/solution', 'solution',
        '/solution_page', 'solution_page',
        '/not_accessible', 'not_accessible',
        '/quit', 'quit'
        )

class quit:
    def GET(self):
        print "QUIT"
        sys.exit()

class main:
    def GET(self):
        raise web.seeother('/magic?page=/summary')
    
    def POST(self):
        return self.GET()

class logout:
    def GET(self):
        web.debug('[USER] %s logged out' % (session.user))
        session.kill()
        raise web.seeother(main_page)

class book:
    def GET(self):
        raise web.seeother('http://mitpress.mit.edu/sicp/full-text/book/book.html')

    def POST(self):
        return self.GET(self)

class reader:
    def GET(self):
        raise web.seeother('http://inst.eecs.berkeley.edu/~cs61as/reader/vol2.html')
    def POST(self):
        return self.GET(self)

class help:
    def GET(self):
        raise web.seeother('http://inst.eecs.berkeley.edu/~cs61as/fa11/help')
    def POST(self):
        return self.GET(self)


class complain:
    def GET(self):
        raise web.seeother('https://inst.eecs.berkeley.edu/~cs61as/complain')
    
    def POST(self):
        return self.GET(self)

class libraryfiles:
    def GET(self):
        raise web.seeother('https://inst.eecs.berkeley.edu/~cs61as/fa11/lib')
    
    def POST(self):
        return self.GET(self)

class lecturefiles:
    def GET(self):
        raise web.seeother('https://inst.eecs.berkeley.edu/~cs61as/fa11/lectures')
    
    def POST(self):
        return self.GET(self)

class admin:
    def GET(self):
        if not isAdmin(session.user):
            raise web.seeother('not_accessible')
        return render.admin(getAdminPage())
    
    def POST(self):
        return self.GET()

class not_accessible:
    def GET(self):
        return "This page is not accessible"

    def POST(self):
        return self.GET()

class course_control:
    def GET(self):
        if not isAdmin(session.user):
            raise web.seeother('/admin_login')
        
        script = """function showHideToggle(id) {
  var obj = document.getElementById("div"+id);
  var obj1 = document.getElementById("sh"+id);
  if (obj.style.display == 'none') {
     obj1.innerHTML = '&#9660;';
    obj.style.display = '';
  } else {
     obj1.innerHTML = '&#9654;';
     obj.style.display = 'none';
  }
}
"""
        js_obj = js(script=script)
        html = (sidebar_css(), js_obj, 
                lesson_layout(content=lesson_content(
                    title="Course Control page",
                    content=getCourseTree(),
                    path=None)))

        return render.course_control(html)
    
    def POST(self):
        return self.GET()

class edit_page:
    def GET(self):
        if not isAdmin(session.user):
            raise web.seeother('/admin_login')

        data = web.input()
        if 'page' in data and 'title' in data and 'code' in data:
            process_edit_page(data)
            raise web.seeother('/course_control')

        edit_page = edit_page_form(data['page'])
        return render.edit_page(edit_page, data['page'])

    def POST(self):
        return self.GET()

class new_page:
    def GET(self):
        if not isAdmin(session.user):
            raise web.seeother('/admin')

        data = web.input()
        if 'page' in data and 'title' in data and 'code' in data:
            make_new_page(data)
            raise web.seeother('/course_control')

        new_page = new_page_form()
        js_obj = js(script=toggle_script)
        return render.new_page(new_page, js_obj, data['page'])

    def POST(self):
        return self.GET()

class course_admin:
    def GET(self):
        f = open(join(course_administration, 'content.html'), 'r')
        content = f.read().strip()
        f.close()
        return render.course_admin(
            (sidebar_css(), 
             lesson_layout(content=page_content(title="Course Administration",
                                                content = content))))

    def POST(self):
        return self.GET()

class magic:
    def GET(self):
        data = web.input()
        print "%s is trying to access %s" % (session.user, data['page'])
        return render.magic(data['page'])
        
    def POST(self):
        return self.GET()

class grades:
    def GET(self):
        return render.grades(getGrades(session.user))

    def POST(self):
        return self.GET()

class sidebar:
    def GET(self):
        return render.sidebar(session.user)
    
    def POST(self):
        return self.GET()

class access:
    def GET(self):
        data = web.input()

        if 'session' in data:
            session_id = data['session']
            session_file = join('..', 'login', 'SSL', 'sessions', session_id)
            if exists(session_file):
                f = open(session_file, 'r')
                text = f.read().split('\n')
                username = text[0]
                t = int(text[1])

                print "trying to make session with username: ", username, " time: ", t

                print "current time: ", int(time() * 1000)

                if abs(time() * 1000 - t + (60 * 1000)) < 600000:
                    session.user = username

        raise web.seeother('/magic?page=/summary')

    def POST(self):
        return self.GET()
        
app = web.application(urls, globals(), True)

if web.config.get('_session') is None:
    session = web.session.Session(app, web.session.DiskStore('sessions'),
                                  initializer={'user': 'Guest'})
    web.config._session = session
else:
    session = web.config._session

if __name__ == "__main__":
    regenerateNext()
    setup_dbs()
    app.run()
