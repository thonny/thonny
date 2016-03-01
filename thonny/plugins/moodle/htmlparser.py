from html.parser import HTMLParser
import urllib.parse

# Search for registered courses, the user ID and the session key
# Equivalent to HTML query: div#myutcourses h3 a[title]
class MoodleCourseListHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self._parsing_courses = False
        self._parsing_course = False
        self._parsing_logininfo = False
        self.courses = []
        self.sesskey = None
        self.user_id = None

    def handle_starttag(self, tag, attrs):
        if self._parsing_courses:
            if tag == 'div':
                self._div_level += 1
            elif tag == 'h3':
                self._parsing_course = True
            elif self._parsing_course and tag == 'a':
                course = {}
                for name,value in attrs:
                    if name == 'title' or name == 'href':
                        course[name] = value
                if 'title' in course:
                    qs = urllib.parse.urlparse(course['href']).query
                    course['id'] = urllib.parse.parse_qs(qs)['id'][0]
                    self.courses.append(course)

        elif tag == 'div':
            if ('id', 'myutcourses') in attrs:
                self._div_level = 0
                self._parsing_courses = True
            elif ('id', 'logininfo'):
                self._div_level = 0
                self._parsing_logininfo = True

        elif self._parsing_logininfo and tag == 'a':
            for name,value in attrs:
                if name == 'href':
                    if 'logout.php?sesskey=' in value:
                        self.sesskey = value[value.index('=')+1:]
                    elif 'profile.php?id=' in value:
                        self.user_id = value[value.index('=')+1:]

    def handle_endtag(self, tag):
        if (self._parsing_courses or self._parsing_logininfo) and tag == 'div':
            self._div_level -= 1
            if self._div_level == 0:
                self._parsing_courses = False
                self._parsing_logininfo = False

        if self._parsing_course and tag == 'h3':
            self._parsing_course = False

# Search "switch role" links
# Equivalent to HTML query: div#settingsnav a[href="switchrole.php?*"]
class MoodleRolesHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self._parsing_roles = False
        self._parsing_link = False
        self.roles = []

    def handle_starttag(self, tag, attrs):
        if self._parsing_roles:
            if tag == 'div':
                self._div_level += 1
            elif tag == 'a':
                role = {}
                for name,value in attrs:
                    if name == 'href' and 'switchrole.php?' in value:
                        #role['url'] = urllib.parse.unquote(value)
                        role['url'] = value
                        self.roles.append(role)
                        self._parsing_link = True
                        break

        elif tag == 'div' and ('id','settingsnav') in attrs:
            self._div_level = 0
            self._parsing_roles = True

    def handle_endtag(self, tag):
        if self._parsing_roles and tag == 'div':
            self._div_level -= 1
            if self._div_level == 0:
                self._parsing_roles = False

        if self._parsing_link and tag == 'a':
            self._parsing_link = False

    def handle_data(self, data):
        if self._parsing_link:
            self.roles[-1]['name'] = data
            self._parsing_link = False

# Search for VPL assignments
# Equivalent to HTML query: section#region-main tbody a[href="view.php?id=*"]
class MoodleVPLAssignmentsHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self._parsing_assignments = False
        self._parsing_assignment = False
        self._parsing_link = False
        self.assignments = []

    def handle_starttag(self, tag, attrs):
        if self._parsing_assignments:
            if tag == 'section':
                self._section_level += 1
            elif tag == 'tbody':
                self._parsing_assignment = True
            elif self._parsing_assignment and tag == 'a':
                assignment = {}
                for name,value in attrs:
                    if name == 'href' and value.startswith('view.php?id='):
                        qs = urllib.parse.urlparse(value).query
                        assignment['id'] = urllib.parse.parse_qs(qs)['id'][0]
                if 'id' in assignment:
                    self.assignments.append(assignment)
                    self._parsing_link = True

        elif tag == 'section' and ('id','region-main') in attrs:
            self._section_level = 0
            self._parsing_assignments = True

    def handle_endtag(self, tag):
        if self._parsing_assignments and tag == 'section':
            self._section_level -= 1
            if self._section_level == 0:
                self._parsing_assignments = False

        if self._parsing_assignment and tag == 'tbody':
            self._parsing_assignment = False

        if self._parsing_link and tag == 'a':
            self._parsing_link = False

    def handle_data(self, data):
        if self._parsing_link:
            self.assignments[-1]['title'] = data

# Search for the web service link of the VPL assignment
# Equivalent to HTML query: section#region-main tbody a[href="view.php?id=*"]
class MoodleVPLServiceLinkHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self, convert_charrefs=True)
        self._parsing_region = False
        self.webservice_url = ""

    def handle_starttag(self, tag, attrs):
        if self._parsing_region:
            if tag == 'section':
                self._section_level += 1
        elif tag == 'section' and ('id','region-main') in attrs:
            self._section_level = 0
            self._parsing_region = True

    def handle_endtag(self, tag):
        if self._parsing_region and tag == 'section':
            self._section_level -= 1
            if self._section_level == 0:
                self._parsing_region = False

    def handle_data(self, data):
        if self._parsing_region:
            if '/mod/vpl/webservice.php' in data:
                self.webservice_url = data
                self._parsing_region = False
