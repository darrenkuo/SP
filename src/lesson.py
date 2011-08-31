import web

from web import form
from format_scheme import format_code
from globals import *
from renderobjects import *
from html import *
from utils import *

from re import match
from re import sub

def getLesson(user, page=''):

    path = '.'
    if page:
        path = convertToRealPath(page)

    data = readLessonData(path)

    f = open(join(course_material, path, 'content.html'), 'r')
    html_code = f.read().strip()
    f.close()
    
    html = clean_html(html_code)
    html = sub('###content_dir###', join(course_material, path), html)

    if 'redirect' in data:
        html = "<meta HTTP-EQUIV='REFRESH' content='0; url=/magic?page=/display?page=%s'>" % (data['redirect'])
    else:
        html = """
<script type='text/javascript'>
function fixiframe() {
document.getElementById('lesson_content').style.width = document.documentElement.clientWidth - 100 + 'px';
resizeFrame(document.getElementById('lesson_content'));
}
function resizeFrame(f) {
f.style.height = f.contentWindow.document.body.scrollHeight + "px";
}
</script>
<style>iframe::-webkit-scrollbar{display:none;}</style>
<iframe width='100%%' height='80%%' frameborder='0' style='overflow:hidden;' src='static/course_material/%s' onload='fixiframe();' id='lesson_content'>
</iframe>""" % (join(path, 'content.html'))
    
    print "done with page:", page

    return (sidebar_css(), 
            lesson_layout(content=lesson_content(title=data['title'], 
                                                 content=html, path=page, 
                                                 renderContent=False, 
                                                 user=user)))

class lesson:
    def GET(self):
        data = web.input()        
        session = web.config._session
        #session = web.config.get('_session')
        if 'page' in data:
            p = data['page']
            ps = p.split('-')
            
            lesson_buttons = None
            if len(ps) >= 2:
                lesson_data = readLessonData(ps[0])
                results = []
                for c in lesson_data['chapters']:
                    t_data = readLessonData(join(ps[0], c))
                    results.append((t_data['title'], ps[0] + "-" + c))
                lesson_buttons = lesson_shortcuts('', lesson_data['title'], 
                                                  results)
            lesson_page = getLesson(session.user, data['page'])
            return render.lesson(lesson_page, lesson_buttons)
        return render.lesson(getLesson(session.user, ''), None)
    
    def POST(self):
        return self.GET()


