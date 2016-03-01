import xml.etree.ElementTree as ET

class MoodleConfig():
    def __init__(self, path):
        self._path = path
        self._conf = {
            'current_role' : None,
            'current_user' : None,
            'users' : {}}
        self.load()

    # Write node attributes to value,
    # store value to data (list) or data[key] (dict)
    def _xml_read_node(self, node, value={}, data=None, key=None):
        value.update(dict(node.attrib))

        if key is None:
            if data is not None:
                data.append(value)
        else:
            if key not in node.attrib and key not in value:
                return
            data[value[key]] = value
            del value[key]

        return value

    def load(self):
        try:
            tree = ET.parse(self._path)
        except FileNotFoundError:
            return

        moodle_node = tree.getroot()
        self._xml_read_node(moodle_node, self._conf)

        for user_node in moodle_node:
            user = self._xml_read_node(user_node, {'courses' : {}}, self._conf['users'], 'name')
            for course_node in user_node:
                course = self._xml_read_node(course_node, {'assignments' : []}, user['courses'], 'id')
                for assignment_node in course_node:
                    #assignment = self._xml_read_node(assignment_node, course['assignments'], 'id')
                    assignment = self._xml_read_node(assignment_node, {}, course['assignments'])
                    for role_node in assignment_node:
                        if 'roles' not in assignment:
                            assignment['roles'] = []
                        assignment['roles'].append(role_node.attrib['name'])

    def _xml_write_node(self, node, value, key=None, keyname=None):
        for key2 in value:
            value2 = value[key2]
            if isinstance(value2, str):
                node.set(key2, value2)

        if keyname is not None:
            node.set(keyname, key)

    def save(self):
        moodle_node = ET.Element('moodle')
        self._xml_write_node(moodle_node, self._conf)

        for name in self._conf['users']:
            user = self._conf['users'][name]
            user_node = ET.SubElement(moodle_node, 'user')
            self._xml_write_node(user_node, user, name, 'name')

            for course_id in user['courses']:
                course = user['courses'][course_id]
                course_node = ET.SubElement(user_node, 'course')
                self._xml_write_node(course_node, course, course_id, 'id')

                for assignment in course['assignments']:
                    assignment_node = ET.SubElement(course_node, 'assignment')
                    self._xml_write_node(assignment_node, assignment)
                    if 'roles' in assignment:
                        for role in assignment['roles']:
                            role_node = ET.SubElement(assignment_node, 'role', name=role)

        tree = ET.ElementTree(moodle_node)
        tree.write(self._path, encoding='utf-8', xml_declaration=True)

    def __getitem__(self, key):
        return self._conf[key]

    def __setitem__(self, key, value):
        self._conf[key] = value

    def __delitem__(self, key):
        del self._conf[key]
