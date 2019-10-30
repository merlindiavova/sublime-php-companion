import sublime
import sublime_plugin

import os
import re

from ..settings import get_setting

class ImportNamespaceCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # Filename to namespace
        file_name = self.view.file_name()

        # Abort if the file is not PHP
        if not file_name.endswith('.php'):
            sublime.error_message('No .php extension')
            return

        # namespace begin at first camelcase dir
        namespace_stmt = os.path.dirname(file_name)

        pattern = re.compile(get_setting('start_dir_pattern', '^.*?((?:\/[A-Z][^\/]*)+)$'))

        namespace_stmt = re.sub(pattern, '\\1', namespace_stmt)
        namespace_stmt = re.sub('/', '\\\\', namespace_stmt)
        namespace_stmt = namespace_stmt.strip('\\')

        # Add an optional prefix - may be per project
        namespacePrefix = get_setting('namespace_prefix', '').strip('\\')
        if namespacePrefix:
            if namespace_stmt:
                namespacePrefix += '\\'
            namespace_stmt = namespacePrefix + namespace_stmt

        # Ensuring PHP tag presence
        php_tag = '<?php'
        php_regex = php_tag.replace('?', '\?')
        php_region = self.view.find(php_regex, 0)
        if php_region.empty():
            line = self.view.line(php_region)
            self.view.insert(edit, 0, php_tag)

        # Removing dst statement
        # dst_region = self.view.find(r'\s*declare\s[\w(]+;', 0)
        # dst_region = self.view.find(r"^\s*declare\(strict_types=1\)", 0)
        # if not dst_region.empty():
        #     self.view.replace(edit, dst_region, '')

        # Removing existing namespace
        namespace_region = self.view.find(r'\s*namespace\s[\w\\]+;', 0)
        if not namespace_region.empty():
            self.view.replace(edit, namespace_region, '')

        # Adding namespace
        namespace_position = get_setting('namespace_position')
        namespace_contents = ' '
        if namespace_position != 'inline':
            namespace_contents = '\n' * get_setting('namespace_blank_lines', 2)
        namespace_contents += 'namespace ' + namespace_stmt + ';'
        if namespace_position != 'inline':
            has_declare = self.view.find(r"^\s*declare\(strict_types=1\)", 0)
            if not has_declare.empty():
                php_docblock_region = has_declare
            else:
                php_regex += r'(\s*\/\*(?:[^*]|\n|(?:\*(?:[^\/]|\n)))*\*\/)?'
                php_docblock_region = self.view.find(php_regex, 0)
        if not php_docblock_region.empty():
            line = self.view.line(php_docblock_region)
            self.view.insert(edit, line.end(), namespace_contents)
