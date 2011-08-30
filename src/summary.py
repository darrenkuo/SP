import web

from web import form
from globals import *
from renderobjects import *
from html import *
from utils import *

def getSummary(user, page=''):
    path = ''
    if page:
        for i in page.split('-'):
            path = join(path, i)

    css_obj = css()
    css_obj.add('sidebar', {'overflow': 'auto',
                            'height': '100%',
                            'width': '15%',
                            'float': 'left',
                            'padding-left': '10px',
                            'padding-top': '50px',})
    css_obj.add('content', {'float': 'left',
                            'width': '75%',
                            'padding-left': '50px',})

    lesson_data = readLessonData(path)
    f = open(join(course_material, 'content.html'), 'r')
    content = div('summary', [html_content(name='', 
                                           content=f.read().strip()),
                              getTableOfContent(lesson_data, '.', 
                                                user, 0, '', lastVisitedPage(user))])
    f.close()

    js_obj = js(script=\
"""function showHideToggle(id) {
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
""")


    return css_obj, js_obj, lesson_layout(content=lesson_content(
            title=lesson_data['title'],
            content=content,
            path=None))

n = 2
def getTableOfContent(lesson_data, path, user, level, page_path, lastVisited=None):
    global n
    #if level >=n:
    #    return 
    components = []
    #print "path:", path
    #print "readable:", checkReadable(lesson_data, user)
    if level > 0:
        #if checkReadable(lesson_data, user):
        
        if len(lesson_data['chapters']) > 0:
            show = True
            if level >= 1:
                show = False
            components.append(showhide(id = 'sh%s' % (str(lesson_data['index'])),
                                       show=show,
                                       script="javascript:showHideToggle(%s)" % (str(lesson_data['index']))))           
        components.append(a(lesson_data['title'],
                            '/magic?page=/display?page=%s' % (page_path),
                            top=True))
    
        #if not checkReadable(lesson_data, user):
        #    components.append(Label("(hidden)"));

        if str(lesson_data['index']) in lastVisited.split('/'):
            components.append(Label("<--- you were here"))
                
    '''
    else:
    components.append(p(lesson_data['title']))
    '''
            
    child_components = []

    for c in lesson_data['chapters']:
        data = readLessonData(join(path, c))
        
        page = '%s-%s' % (page_path, c)
        if page_path == '':
            page = str(c)

        o = getTableOfContent(data, join(path, c), user,
                              level + 1, page, lastVisited)

        if o:
            child_components.append(o)
            '''
            if level == 0:
                child_components.append(Br())
            '''

    if level >= 1:
        components.append(div('div%s' % (str(lesson_data['index'])), child_components, style='display : none'))
    else:
        components.append(div('div%s' % (str(lesson_data['index'])), child_components))


    if level == 0:
        return ol('', components)
    else:
        return ul('', components)

class summary:
    def GET(self):
        data = web.input()
        session = web.config._session
        print "user:", session.user
        if 'page' in data:
            return render.summary(getSummary(session.user, data['page']))
        else:
            return render.summary(getSummary(session.user, ''))
    
    def POST(self):
        return self.GET()

# window.open(<address>, <name>, <features>)
# features = 'left=20, top=20, width=500, height=500'
