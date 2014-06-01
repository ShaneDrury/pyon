import hashlib
from django.utils import six
from jinja2 import Environment, FileSystemLoader
import simplejson
import os
import logging
import time
from importlib import import_module
from django.conf import settings
log = logging.getLogger(__name__)


class Project(object):
    def __init__(self, name=None, dump_dir=None,
                 db_path=None):
        self.name = name or time.strftime("%Y%m%d-%H%M%S")
        self.measurement_results = {}
        self.dump_dir = dump_dir
        self.db_path = db_path
        self.report_name = 'report.html'
        self.dump_name = 'dump.json'
        self.template_env = None
        self.prepare_template_env()
        self.measurements = []
        self.parsers = []
        self.populate_parsers()
        self.populate_measurements()

    def _generic_main(self, objects, name_stem, short_name):

        list_name = "{}_list".format(short_name)
        results = "{}_results".format(name_stem)
        store_results = True

        try:
            getattr(self, results)
        except AttributeError:
            log.info("No {} attribute in Project class. "
                         "Output from {} objects will not be stored."
                         .format(results, name_stem))
            store_results = False
            
        for obj in objects:
            for sub_obj in obj[list_name]:
                object_name = obj['name']
                if sub_obj['name']:
                    object_name = os.path.join(object_name,
                                               sub_obj['name'])
                log.info("Doing {} {}".format(name_stem, object_name))
                objekt = sub_obj[name_stem]
                obj_results = objekt()
                template_name = sub_obj.get('template_name', None)

                if store_results:
                    getattr(self, results)[object_name] = obj_results

                    if self.dump_dir and obj_results is not None:
                        self.dump_result(object_name, obj_results)

                    if template_name:
                        template = self.get_template(template_name)
                        self.write_report(template, object_name,
                                          time.strftime("%c"), obj_results)
                    
    def main(self):
        log.debug("Running Project: {}".format(self.name))
        self._generic_main(self.measurements, "measurement", "meas")

    def populatedb(self):
        log.debug("Populating Project Databse: {}".format(self.name))
        self._generic_main(self.parsers, "parser", "parse")
        
    def prepare_template_env(self):
        template_folders = settings.TEMPLATE_DIRS
        self.template_env = Environment(
            loader=FileSystemLoader(template_folders))

    def get_template(self, template_name):
        return self.template_env.get_template(template_name)

    def _populate(self, root_variable, name_stem, short_name):
        """Generic variable population function"""
        mod = import_module(root_variable)
        #  Get the attribute `measurements` from the `ROOT_MEASUREMENTS`
        #  module.
        plural = '{}s'.format(name_stem)
        list_name = '{}_list'.format(short_name)
        objects = getattr(mod, plural)
        for obj in objects:  # This is an iterable, so iterate over it.
            o = obj[name_stem]  # Get the `Runner` value of the dict
            if isinstance(o, six.string_types):
                #  If it's a string, assume it is the name of a module in
                #  another package.
                sub_mod = import_module(o)
                sub_obj_list = getattr(sub_mod, plural)
                obj_dict = {'name': obj['name'],
                            list_name: sub_obj_list}
                getattr(self, plural).append(obj_dict)
            else:
                #  Otherwise, it should be an instance of a Runner
                try:
                    the_list = ({'name': None, name_stem: o,
                                 'template_name': obj['template_name']},)
                except KeyError:
                    the_list = ({'name': None, name_stem: o,},)
                
                obj_dict \
                  = {'name': obj['name'], list_name: the_list}
                getattr(self, plural).append(obj_dict)

    def populate_measurements(self):
        """
        Traverse from the root measurement module and get all the measurements.
        """
        self._populate(settings.ROOT_MEASUREMENTS, 'measurement', 'meas')
        
    def populate_parsers(self):
        """
        Traverse from the root measurement module and get all the measurements.
        """
        self._populate(settings.ROOT_PARSERS, 'parser', 'parse')

    def dump_result(self, measurement_name, measurement_results):
        dump_path = os.path.join(self.dump_dir, measurement_name)
        if not os.path.exists(dump_path):
            os.makedirs(dump_path)
        log.info("Dumping results to {}".format(dump_path))
        to_dump = self.dumps(measurement_name, measurement_results)
        with open(os.path.join(dump_path, self.dump_name), 'w') as f:
            simplejson.dump(to_dump, f, namedtuple_as_object=True)

    def write_report(self, template, measurement_name, date,
                     measurement_results):
        to_report = {}
        for k, v in measurement_results.items():
            vv = v._asdict()
            vv['hash'] = self.hash_name(k)
            to_report[k] = vv
        rendered = self.render_template(template, measurement_name, date,
                                        to_report)
        report_dir = os.path.join(self.dump_dir, measurement_name)
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
        with open(os.path.join(report_dir, self.report_name), 'w') as f:
            f.write(rendered)

    @staticmethod
    def hash_name(result_name):
        result_name = str(result_name)
        hash_object = hashlib.md5(result_name.encode('utf-8'))
        hashed_name = hash_object.hexdigest()
        return hashed_name

    @staticmethod
    def read_result(result_path):
        with open(result_path, 'r') as f:
            result = simplejson.load(f, namedtuple_as_object=True)
        return result

    def dumps(self, measurement_name, results):
        to_dump = self._sanitize_dic(results)
        to_dump['date'] = time.strftime("%c")
        to_dump['measurement_name'] = measurement_name
        return to_dump

    @staticmethod
    def render_template(template, measurement_name, date, results):
        template_dic = {
            'title': measurement_name,
            'measurement_results': results,
            'measurement_date': date,
        }
        rendered = template.render(**template_dic)
        return rendered

    @staticmethod
    def _sanitize_dic(dic):
        new_dic = {}
        for key in dic.keys():
            if type(key) is not str:
                try:
                    new_dic[str(key)] = dic[key]
                except:
                    try:
                        new_dic[repr(key)] = dic[key]
                    except:
                        log.debug("Sanitize failed for {}".format(key))
                        pass
            else:
                new_dic[key] = dic[key]
        return new_dic
