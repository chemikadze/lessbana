import re

from ConfigParser import ConfigParser
import yaml
import jinja2
import logging

class Route(object):

    def __init__(self, pattern, data):
        self.pattern = pattern
        self.data = data

    def __repr__(self):
        return "route %s: %s" % (self.pattern, self.data)

    def compile(self, context):
        result = {}
        for key, value in self.data.iteritems():
            if key in ['query', 'sort']:
                result[key] = self._apply_template(value, context)
            elif key == 'elasticsearch_url':
                match = value.split(":")
                parsed_value = {'host': match[0]}
                if len(match) > 1:
                    parsed_value['port'] = match[1]
                result[key] = [parsed_value]
            else:
                result[key] = value
        return result

    def _apply_template(self, template, context):
        def _render(template, context):
            return jinja2.Template(template).render(context)
        if isinstance(template, basestring):
            return _render(template, context)
        elif isinstance(template, dict):
            result = {}
            for key, value in template.iteritems():
                result[_render(key, context)] = self._apply_template(value, context)
            return result
        elif isinstance(template, list):
            result = []
            for value in template:
                result.append(self._apply_template(value, context))
            return result
        else:
            return template

class Router(object):

    def __init__(self, src):
        self._routes = []
        config = yaml.load(src)
        default_dict = config.get('default')
        for pattern in config.get('patterns', list()):
            section = pattern.keys()[0]
            values = pattern.values()[0]
            if section == 'default':
                continue
            data = {}
            data.update(default_dict)
            if values:
                data.update(values)
            route = Route(section, data)
            self._routes.append(route)
        logging.debug("Routes parsed: %s" % (self._routes,))

    def match(self, path):
        for route in self._routes:
            match = re.match(route.pattern, path)
            if match:
                break
        else:
            return None
        return route.compile(match.groupdict())