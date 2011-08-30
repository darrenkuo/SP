from os.path import join

from globals import *
from html import *
from utils import *

class css:
    def __init__(self):
        self.css_mapping = {}

    def add(self, id, mapping):
        self.css_mapping[id] = mapping

    def render(self):
        output = '<style type="text/css">\n'
        for i in self.css_mapping:
            output += '\t#%s { \n' % (i)
            for j in self.css_mapping[i]:
                output += '\t\t%s: %s;\n' % (j, self.css_mapping[i][j])
            output += '\t}\n'

        return output + '\t</style>'

class sidebar_css(css):
    def __init__(self):
        css.__init__(self)
        self.add('sidebar', {#'overflow': 'auto',
                                         'height': '100%',
                                         'width': '15%',
                                         'float': 'left',
                                         'padding-left': '10px',
                                         'padding-top': '50px',})
        self.add('content', {'float': 'left',
                                         'height': '100%',
                                         'width': '80%',                      
                                         'padding-left': '50px',})

class quiz_js(js):
    def __init__(self, page, script='', question_type={}, *validators, **attrs):
        post_to_url = """function post_to_url(path, params, method) {
        method = method || "post"; // Set method to post by default, if not specified.
        
    // The rest of this code assumes you are not using a library.
    // It can be made less wordy if you use one.
    var form = document.createElement("form");
    form.setAttribute("method", method);
    form.setAttribute("action", path);

    for(var key in params) {
        var hiddenField = document.createElement("input");
        hiddenField.setAttribute("type", "hidden");
        hiddenField.setAttribute("name", key);
        hiddenField.setAttribute("value", params[key]);

        form.appendChild(hiddenField);
    }


    document.body.appendChild(form);
    form.submit();
  }
    """

        checked_value = """
function getCheckedValue(radioObj) {
if(!radioObj)
return "";
var radioLength = radioObj.length;
if(radioLength == undefined)
if(radioObj.checked)
return radioObj.value;
else
return "";
for(var i = 0; i < radioLength; i++) {
if(radioObj[i].checked) {
return radioObj[i].value;
}
}
return "";
}
    """
        submit_func = "function submit() { var data={};data['submitting']=true;"
        
        for q, t in question_type.iteritems():
            if t == 'r':
                submit_func += "data[%d] = getCheckedValue(document.forms['q%d-form'].elements['q%d']);" % (q, q, q)
            elif t == 'b':
                submit_func += "data[%d] = document.getElementById('q%d').value;" % (q, q)

        submit_func += 'post_to_url("/quiz?page=%s", data);}' % (page)

        script += post_to_url
        script += checked_value
        script += submit_func

        js.__init__(self, script)

class lesson_sidebar:
    def render(self):
        links = [('Main', '/summary'),
                 ('Administrative', '/course_admin'),
                 ('Solutions', '/solution'),
                 ('Complaint form', 'https://inst.eecs.berkeley.edu/~cs61a/complain'),
                 ('Reader', 'http://inst.eecs.berkeley.edu/~cs61a/reader/vol2.html'),
                 ('Logout', '/logout')]

        href = '\t<a href="%s">%s</a></br>'
        return ('<div id="sidebar">' +
                '\n'.join(map(lambda x: href % (x[1], x[0]),
                             links)) + 
                '<br/><br/><br/>' + 
                '<a href="http://mitpress.mit.edu/sicp/full-text/book/book.html" target="_blank"><img height="40%" width="200px" src="http://mitpress.mit.edu/sicp/full-text/book/cover.jpg"/></a>' +
                '</div>')

class admin_sidebar:
    def render(self):
        links = [('Main', '/summary'),
                 ('Course Administration', '/course_admin'),
                 ('Course Control', '/course_control'),
                 ('Logout', '/logout')]

        href = '\t<a href="%s">%s</a></br>'
        return ('<div id="sidebar">' +
                '\n'.join(map(lambda x: href % (x[1], x[0]),
                             links)) + 
                '</div>')

def makeNewPath(previous_path, path):
    if previous_path and path != '':
        return '/display?page=%s' % (previous_path + '-' + path)
    elif previous_path:
        return '/display?page=%s' % (previous_path)
    else:
        return '/display?page=%s' % (path)
"""
def findPreviousNext(path, user):
    from utils import readLessonData
    from utils import convertToRealPath
    from utils import checkReadable

    if path == '':
        return (None, '/summary')
    else:
        stack = []
        current = path.strip().split('-')[-1]
        current_path = '/'.join(path.strip().split('-'))

        lesson_data = readLessonData(current_path)

        stack.extend(map(lambda x: (x, path), lesson_data['chapters']))
        for c, p in stack:
            new_path = join(convertToRealPath(p), c)
            new_lesson_data = readLessonData(new_path)
            new_path_fake = '%s-%s' % (p, c)
            #print 'checking path: ', new_path_fake
            if checkReadable(new_lesson_data, user):
                return (None, '/magic?page=/display?page=%s' % (new_path_fake))

            for c1 in new_lesson_data['chapters']:
                stack.insert(0, (c1, new_path_fake))

        #print 'path', path
        parent_path = path
        while True:
            indices = parent_path.strip().split('-')
            temp_parent_path = '/'.join(indices[:-1])
            current = indices[-1]
            parent_path = '-'.join(parent_path.strip().split('-')[:-1])
            parent_lesson_data = readLessonData(temp_parent_path)

            print parent_path
            if parent_path == '.' or parent_path == '':
                return (None, '/summary')
            
            for i in range(len(parent_lesson_data['chapters'])):
                print parent_lesson_data['chapters'][i], current
                if parent_lesson_data['chapters'][i] == current:
                    if (i + 1) == len(parent_lesson_data['chapters']):
                        print 'breaking!'
                        break
                    else:
                        new_path = join(temp_parent_path,
                                        parent_lesson_data['chapters'][i+1])
                        page_path = '-'.join(new_path.split('/'))
                        temp_lesson_data = readLessonData(new_path)
                        #print 'checking parent path:', new_path
                        if checkReadable(temp_lesson_data, user):
                            print 'checked readable for', new_path
                            return (None, '/magic?page=/display?page=%s' % (page_path))
                        else:
                            print 'find next with', new_path
                            return findPreviousNext(new_path, user)
"""
        
class unreadable_content:
    def render(self):
        return '<h2>This page is not accessible at the moment. It might be because unsatified requirements</h2>'

class page_content:
    def __init__(self, title=None, content=None):
        self.title = title
        self.content = content

    def render(self):
        output = '<div id="content">\n'
        if self.title:
            output += '<h2>%s</h2>' % (self.title)

        output += self.content + '</div>'

        return output

class lesson_content:
    def __init__(self, title=None, content=None, path=None, renderContent=True, user=None):
        self.title = title
        self.content = content
        self.path = path
        self.renderContent = renderContent
        self.user = user

    def render(self):
        output = '<div id="content">'

        if self.title:
            output += '<h2>%s</h2>' % (self.title)
        
        if self.content:
            if not self.renderContent:
                output += self.content
            else:
                output += self.content.render()

        if self.path != None and self.user:
            next = findPreviousNext(self.path, self.user)
            output += '</p>'
            
            if next:
                output += '<P align="right">'
                output += '<a class="chapter" href="%s" target="_top">Next&raquo;</a>' % (next)
                output += '</P>'

        return output + '</div>'

class lesson_layout:
    def __init__(self, content=lesson_content()):
        self.content = content

    def render(self):
        if type(self.content) == str:
            return self.content

        return self.content.render()
