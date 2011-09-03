import web


from os import walk
from os.path import exists
from os.path import join
from re import search

from globals import *
from html import html_content
from utils import storeAssignmentTime, sawSolution

solution_dir = '/home/ff/cs61as/solutions'

def submittedAssignment(assignment, user):
    if exists(join(solution_dir, assignment)):
        files = walk('/home/ff/cs61as/grading/submissions/%s' % (assignment)).next()[2]
        for f in files:
            if search(user, f):
                return True

    return False

class solution:
    def GET(self):
        session = web.config._session
        assignments = walk('/home/ff/cs61as/grading/submissions').next()[1]

        seen = []
        unseen = []
        
        output = ""
        for a in assignments:
            files = walk('/home/ff/cs61as/grading/submissions/%s' % (a)).next()[2]
            for f in files:
                if search(session.user, f):
                    if sawSolution(a, session.user):
                        print 'seen', a
                        seen.append(a)
                    else:
                        print 'unseen', a
                        unseen.append(a)

        seen_output = ""
        unseen_output = ""
        if seen or unseen:
            if seen:
                for s in seen:
                    seen_output += '<a target="_top" href="/magic?page=/solution_page?assignment=%s">%s</a></br>' % (s, s)
                    
            if unseen:
                for s in unseen:
                    unseen_output += '<a target="_top" href="/magic?page=/solution_page?assignment=%s">%s</a></br>' % (s, s)

        if seen_output or unseen_output:
            seen_content = None
            if seen_output:
                seen_content = html_content('', seen_output)

            unseen_content = None
            if unseen_output:
                unseen_content = html_content('', unseen_output)
                
            return render.solution(seen_content, unseen_content)
        else:
            return render.solution(None, None)

    def POST(self):
        return self.GET()

class solution_page:
    def GET(self):
        data = web.input()
        session = web.config._session

        if 'assignment' in data:
            page = data['assignment']
            if (exists(join(solution_dir, page)) and
                submittedAssignment(page, session.user)):
                storeAssignmentTime(page, session.user)
                f = open(join(solution_dir, page), 'r')
                content = html_content('', f.read().replace('\n', '</br>'))
                f.close()
                return render.solution_page(content)

        return render.solution_page(html_content('', 'Well..this is a blank page'))


    def POST(self):
        return self.GET()
