# -*- coding: utf-8 -*-

from enum import Enum
import os
import threading
import tkinter as tk
from tkinter import Button, Entry, Frame, Label, Listbox, OptionMenu, StringVar
import urllib.parse
import urllib.request

from thonny.globals import get_workbench
from thonny.ui_utils import ScrollableFrame, TreeFrame
from thonny.plugins.moodle.config import MoodleConfig
from thonny.plugins.moodle.htmlparser import *
from thonny.plugins.moodle.vpl_exercise_proxy import mod_vpl_info
from thonny import THONNY_USER_DIR

class MoodleViewState(Enum):
    initial = 1
    add = 2
    login = 3

# Passes on the session cookie during
# redirection from the Moodle login page
class RedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        cookie = headers.get('Set-Cookie')
        if cookie is not None:
            session_cookie = cookie.split(";")[0]
            req.add_header('Cookie', session_cookie)
        return urllib.request.HTTPRedirectHandler.redirect_request(self,
            req, fp, code, msg, headers, newurl)

class MoodleView(ScrollableFrame):
    def __init__(self, master):
        ScrollableFrame.__init__(self, master)
        self.canvas.config(bg='SystemButtonFace')
        self.interior.config(bg='SystemButtonFace')

        # Initial configuration
        self._user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'
        self._moodle_url = 'https://moodle.ut.ee'

        # Load Moodle configuration file from the user directory
        path = os.path.join(THONNY_USER_DIR, 'moodle_assignments.xml')
        self._conf = MoodleConfig(os.path.expanduser(path))

        # Course browser
        self._courses_list = TreeFrame(self.interior, columns=())
        self._courses_list.tree.heading('#0', text="Ülesanne", anchor=tk.W)
        self._courses_list.tree['show'] = ('tree') # 'headings'
        self._courses_list.tree.bind("<<TreeviewSelect>>", self.__assignment_selected)
        self._courses_list.grid(row=0, sticky=tk.W+tk.E, padx=(0,10))

        self._browser_buttons = Frame(self.interior)
        self._add_assignment_btn = Button(self._browser_buttons, text="Lisa", command=self.add_assignment)
        self._remove_btn = Button(self._browser_buttons, text="Eemalda", command=self.remove_assignment, state=tk.DISABLED)
        self._roles_option_var = StringVar()
        self._roles_option = OptionMenu(self._browser_buttons, self._roles_option_var, ())

        self._add_assignment_btn.grid(row=0, column=0, sticky=tk.NW, padx=(10,0), pady=2)
        self._remove_btn.grid(row=0, column=1, sticky=tk.NW, padx=(10,0), pady=2)
        self._roles_option.grid(row=0, column=2, sticky=tk.NE, padx=(10,0))
        self._roles_option.grid_remove()
        self._browser_buttons.grid(row=1, sticky=tk.W+tk.E, pady=5)

        # Separator
        self._separator = Frame(self.interior, height=2, bd=1, relief=tk.SUNKEN)
        self._separator.grid(row=2, sticky=tk.W+tk.E, pady=(0,10))

        # Assignment data form
        self._assignment_form = Frame(self.interior, padx=10)
        self._assignment_desc = Label(self._assignment_form, justify=tk.LEFT)
        self._assignment_desc.grid(row=0, sticky=tk.W+tk.E)
        self._assignment_form.grid(row=3, sticky=tk.NW)

        # Login form
        self._login_form = Frame(self.interior, padx=10)
        self._login_els = {}
        self._login_els['username_label'] = Label(self._login_form, text="Kasutajanimi")
        self._login_els['username_entry'] = Entry(self._login_form)
        self._login_els['password_label'] = Label(self._login_form, text="Parool")
        self._login_els['password_entry'] = Entry(self._login_form, show="*")
        self._login_els['login_button'] = Button(self._login_form, text="Lisa Moodle'ist", command=self.login)
        self._login_els['manual_button'] = Button(self._login_form, text="Lisa käsitsi", command=self.add_assignment_manual)

        self._login_els['username_label'].grid(row=0, sticky=tk.NW)
        self._login_els['username_entry'].grid(row=1, sticky=tk.NW)
        self._login_els['password_label'].grid(row=2, sticky=tk.NW)
        self._login_els['password_entry'].grid(row=3, sticky=tk.NW)
        self._login_els['login_button'].grid(row=4, sticky=tk.NW, pady=5)
        self._login_els['manual_button'].grid(row=5, sticky=tk.NW, pady=5)
        self._login_els['password_entry'].bind('<Return>', self.__login_entry_return_key)
        self._login_form.grid(row=3, sticky=tk.NW)

        # Status text
        self._status_label = Label(self.interior, text="", fg='black')
        self._status_label.grid(row=4, sticky=tk.NW)

        # Install redirect handler
        redirect_handler = RedirectHandler()
        opener = urllib.request.build_opener(redirect_handler)
        urllib.request.install_opener(opener)

        # Show user and assignments
        self.set_state(MoodleViewState.initial)
        self.display_moodle_assignments()

        # Open assignment add view if no assignments have been added
        if self._conf['current_user'] is None:
            self.set_state(MoodleViewState.add)
        elif len(self._conf['users'][self._conf['current_user']]['courses']) == 0:
            self.set_state(MoodleViewState.add)
        else:
            self.set_state(MoodleViewState.initial)

    def set_state(self, state):
        if state == MoodleViewState.initial:
            login_state = tk.NORMAL
            login_show = True
            add_show = False
        elif state == MoodleViewState.add:
            login_state = tk.NORMAL
            login_show = True
            add_show = True
        elif state == MoodleViewState.login:
            login_state = tk.DISABLED
            login_show = True
            add_show = True

        if add_show:
            self._add_assignment_btn.config(relief=tk.SUNKEN)
            self._login_form.grid()
            for el in self._login_els:
                self._login_els[el].config(state=login_state)
            self._assignment_desc.grid_remove()
        else:
            self._add_assignment_btn.config(relief=tk.RAISED)
            self._login_form.grid_remove()
            self._assignment_desc.grid()

        self._login_els['manual_button'].config(state=tk.DISABLED)

    def add_assignment(self):
        if self._add_assignment_btn.cget('relief') == tk.RAISED:
            self.set_state(MoodleViewState.add)
        else:
            self.set_state(MoodleViewState.initial)

    def add_assignment_manual(self):
        # TODO
        pass

    def remove_assignment(self):
        # TODO
        pass

    def create_url_request(self, url, data=None):
        req = urllib.request.Request(url, data=data)
        req.add_header('Accept', "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
        req.add_header("Accept-Language", "et,et-EE;q=0.8,en-US;q=0.5,en;q=0.3")
        req.add_header("User-Agent", self._user_agent)
        if self._session_cookie is not None:
            req.add_header("Cookie", self._session_cookie)
        if data is not None:
            req.add_header('Content-Type', "application/x-www-form-urlencoded;charset=utf-8")
        return req

    def login(self):
        self._status_label.config(text="Sisselogimine...", fg='black')
        self.set_state(MoodleViewState.login)

        t = threading.Thread(target=self.login_thread)
        t.start()

    def login_thread(self):
        self._sesskey = None
        self._session_cookie = None

        # Get and verify username/password
        username = self._login_els['username_entry'].get()
        password = self._login_els['password_entry'].get()
        if not username or not password:
            self._status_label.config(text="Sisesta Moodle'i kasutajanimi ja parool", fg='red')
            self.set_state(MoodleViewState.add)
            return

        # Fetch session ID from Moodle login page
        login_url = self._moodle_url + "/login/index.php"
        req = self.create_url_request(login_url)
        try:
            with urllib.request.urlopen(req) as response:
                cookie = response.headers.get('Set-Cookie')
                self._session_cookie = cookie.split(";")[0]
        except:
            self._status_label.config(text="Sisselogimise viga!", fg='red')
            self.set_state(MoodleViewState.add)
            return

        # POST login request
        data = {'username' : username, 'password' : password}
        data = urllib.parse.urlencode(data).encode('utf-8')

        req = self.create_url_request(login_url, data)
        req.add_header('Referer', login_url)
        try:
            with urllib.request.urlopen(req) as response:
                page = response.read()
        except:
            self._status_label.config(text="Sisselogimise viga!", fg='red')
            self.set_state(MoodleViewState.add)
            return
        self._session_cookie = req.headers.get('Cookie')

        # Parse response for courses list and session key
        parser = MoodleCourseListHTMLParser()
        parser.feed(page.decode('utf-8'))
        if parser.sesskey is None:
            self.logout()
            self._status_label.config(text="Autentimine ebaõnnestus!", fg='red')
            self.set_state(MoodleViewState.add)
            return
        self._sesskey = parser.sesskey
        self._user_id = parser.user_id

        self._status_label.config(text="Ülesannete allalaadimine...", fg='black')
        self.set_state(MoodleViewState.initial)

        # Merge parser output with existing data
        # If user doesn't exist, create one
        if username in self._conf['users']:
            user = self._conf['users'][username]
        else:
            user = {
                'id' : self._user_id,
                'courses' : {}}
            self._conf['users'][username] = user
        self._conf['current_user'] = username

        # If courses don't exist, create them
        for course_p in parser.courses:
            course = None
            course_id = course_p['id']
            if course_id in user['courses']:
                course = user['courses'][course_id]
            assignments_p = self.get_vpl_assignments(course_id)
            if course is None:
                if len(assignments_p) == 0:
                    continue
                course = course_p
                course['assignments'] = []
                user['courses'][course_id] = course
                course_ui_id = self._courses_list.tree.insert("", tk.END, text=course['title'], open=True)
            else:
                course.update(course_p)
                # TODO: Remove existing assignments if they are no longer on Moodle?
                if len(assignments_p) == 0:
                    continue

            # If assignments don't exist, create them
            # The web service URL can only be used within the Moodle session
            for assignment_p in assignments_p:

                # Look for existing assignment
                assignment = None
                for assignment_u in course['assignments']:
                    if assignment_u['id'] == assignment_p['id']:
                        assignment = assignment_u
                        break

                if assignment is None:
                    assignment = assignment_p
                    course['assignments'].append(assignment)
                    if self._conf['current_role'] is None and 'roles' in assignment:
                        self._conf['current_role'] = assignment['roles'][0]

                    # Update UI
                    if 'roles' not in assignment or self._conf['current_role'] in assignment['roles']:
                        self._courses_list.tree.insert(course_ui_id, tk.END, text=assignment['title'],
                            tags=[username, course_id, assignment['id']])
                else:
                    # Update existing data
                    assignment['title'] = assignment_p['title']
                    if 'roles' in assignment_p:
                        assignment['roles'] = assignment_p['roles']
                    elif 'roles' in assignment:
                        del assignment['roles']

                if 'webservice_url' not in assignment:
                    webservice_url = self.get_vpl_webservice_url(assignment)
                    if webservice_url is not None:
                        assignment['webservice_url'] = webservice_url

        # Logging out causes VPL links to break
        # self.logout()
        self._conf.save()

        # Clear password data and update UI state
        self._login_els['password_entry'].delete(0, tk.END)
        self._status_label.config(text="Ülesanded uuendatud", fg='black')
        self.set_state(MoodleViewState.initial)
        self.display_moodle_assignments()

    def logout(self):
        if self._sesskey is not None:
            logout_url = self._moodle_url + "/login/logout.php"

            # POST logout request
            data = {'sesskey' : self._sesskey}
            data = urllib.parse.urlencode(data).encode('utf-8')

            req = self.create_url_request(logout_url, data)
            try:
                with urllib.request.urlopen(req) as response:
                    response.read()
            except:
                pass
            self._sesskey = None

        self._session_cookie = None

    # Navigate to switchrole.php and return the redirect page
    def switch_role(self, url):
        req = self.create_url_request(url)
        try:
            with urllib.request.urlopen(req) as response:
                page = response.read()
            return page
        except:
            self._status_label.config(text="Moodle'i lugemise viga!", fg='red')
            self.set_state(MoodleViewState.initial)
            return None

    # Set the 'switchrole' parameter to 0 and do the switch
    def switch_role_default(self, url):
        switchrole_index = url.index('switchrole=') + len('switchrole=')
        url = url[:switchrole_index] + '0' + url[switchrole_index+1:]
        self.switch_role(url)

    # Download VPL assignments of the course
    def get_vpl_assignments(self, course_id):
        vpl_assignments_url = self._moodle_url + '/mod/vpl/index.php?id=' + course_id
        req = self.create_url_request(vpl_assignments_url)
        try:
            with urllib.request.urlopen(req) as response:
                page = response.read()
        except:
            self._status_label.config(text="Moodle'i lugemise viga!", fg='red')
            self.set_state(MoodleViewState.initial)
            return []

        # Enumerate all roles (request was made using the default role)
        page = page.decode('utf-8')
        parser = MoodleRolesHTMLParser()
        parser.feed(page)
        roles = parser.roles

        if len(roles) == 0:
            return []
        elif len(roles) == 1:
            parser = MoodleVPLAssignmentsHTMLParser()
            parser.feed(page)
            return parser.assignments

        # Switch to different roles and check for which the assignment is available
        assignments = []
        for role in roles:
            page = self.switch_role(role['url'])
            page = page.decode('utf-8')
            parser = MoodleVPLAssignmentsHTMLParser()
            parser.feed(page)
            for assignment_p in parser.assignments:
                assignment_exists = False
                for assignment in assignments:
                    if assignment['id'] == assignment_p['id']:
                        assignment_exists = True
                        assignment['roles'].append(role['name'])
                if not assignment_exists:
                    assignment_p['roles'] = [role['name']]
                    assignments.append(assignment_p)
            self.switch_role_default(roles[0]['url'])

        # No need to manage a single role
        for assignment in assignments:
            if len(assignment['roles']) <= 1:
                del assignment['roles']

        return assignments

    def get_vpl_webservice_url(self, assignment):
        assignment_id = assignment['id']
        vpl_service_url = self._moodle_url + '/mod/vpl/views/show_webservice.php?id=' + assignment_id
        req = self.create_url_request(vpl_service_url)
        try:
            with urllib.request.urlopen(req) as response:
                page = response.read()
        except:
            self._status_label.config(text="Moodle'i lugemise viga!", fg='red')
            self.set_state(MoodleViewState.initial)
            return None

        page = page.decode('utf-8')
        parser = MoodleVPLServiceLinkHTMLParser()
        parser.feed(page)
        if parser.webservice_url is not None:
            return parser.webservice_url

        # URL not given, switch to a suitable role
        if 'roles' not in assignment:
            return None
        parser = MoodleRolesHTMLParser()
        parser.feed(page)
        roles = parser.roles
        for role in roles:
            if role['name'] in assignment['roles']:
                page = self.switch_role(role['url'])
                break

        page = page.decode('utf-8')
        parser = MoodleVPLServiceLinkHTMLParser()
        parser.feed(page)

        self.switch_role_default(roles[0]['url'])

        return parser.webservice_url

    def display_moodle_assignments(self):
        # Clear courses list
        for child_id in self._courses_list.tree.get_children():
            self._courses_list.tree.delete(child_id)

        # Add user's courses and assignments
        if self._conf['current_user'] is None:
            return
        user = self._conf['users'][self._conf['current_user']]
        for course_id in user['courses']:
            course = user['courses'][str(course_id)]
            course_ui_id = self._courses_list.tree.insert("", tk.END, text=course['title'], open=True)
            for assignment in course['assignments']:
                # If assignment requires a role to view it and no role has been selected,
                # then select the first appropriate role.
                if self._conf['current_role'] is None and 'roles' in assignment:
                    self._conf['current_role'] = assignment['roles'][0]
                if 'roles' in assignment and self._conf['current_role'] not in assignment['roles']:
                    continue
                self._courses_list.tree.insert(course_ui_id, tk.END, text=assignment['title'],
                    tags=[self._conf['current_user'], course_id, assignment['id']])

        self.display_moodle_role()

        # Fill login form
        self._login_els['username_entry'].delete(0, tk.END)
        self._login_els['username_entry'].insert(tk.END, self._conf['current_user'])

    def display_moodle_role(self):
        if self._conf['current_user'] is None:
            self._roles_option.grid_remove()
            return

        menu = self._roles_option['menu']
        menu.delete(0, 'end')

        roles = []
        courses = self._conf['users'][self._conf['current_user']]['courses']
        for course_id in courses:
            course = courses[course_id]
            for assignment in course['assignments']:
                for role in assignment.get('roles', []):
                    if role not in roles:
                        roles.append(role)
                        menu.add_command(label=role,
                            command=lambda item=role: self.select_role_cmd(item))

        self._roles_option_var.set(self._conf['current_role'])
        self._roles_option.grid()

    def select_role_cmd(self, role):
        if self._conf['current_role'] == role:
            return

        self._conf['current_role'] = role
        self._roles_option_var.set(role)
        self.display_moodle_assignments()

    def __assignment_selected(self, event=None):
        selected = self._courses_list.tree.selection()
        if len(selected) == 0:
            self._assignment_desc.config(text="")
            return
        selected = self._courses_list.tree.item(selected[0])
        tags = selected['tags']
        if len(tags) == 0:
            self._assignment_desc.config(text="")
            return

        user = self._conf['users'][tags[0]]
        course = user['courses'][str(tags[1])]
        for assignment in course['assignments']:
            if assignment['id'] == str(tags[2]):
                break
        if 'webservice_url' not in assignment:
            self._assignment_desc.config(text="")
            print('web')
            # TODO
            return
        webservice_url = assignment['webservice_url']
        self._assignment_desc.config(text=selected['text'] + "\nKirjelduse allalaadimine...\n" + webservice_url)
        info = mod_vpl_info(webservice_url)
        print(info)
        if 'exception' in info and info['errorcode'] == 'invalidtoken':
            self._assignment_desc.config(text=selected['text'] + "\n" + webservice_url + "\nSessioon on aegunud!")
            del assignment['webservice_url']
            # TODO: delete all assignment URLs
        else:
            self._assignment_desc.config(text=selected['text'] + "\n" + webservice_url + "\n" + info['intro'])
        

    def __login_entry_return_key(self, event=None):
        self.login()

def load_plugin():
    get_workbench().add_view(MoodleView, "Moodle", 'nw')
