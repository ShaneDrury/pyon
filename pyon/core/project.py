import copy
import hashlib
import re
from django.utils import six
from jinja2 import Environment, FileSystemLoader
import pickle
import os
import logging
import time
from importlib import import_module
from django.conf import settings
import matplotlib.pyplot as plt
from pyon.core.cache import cache_data
from pyon.core.util import dict_to_ordered_dict

log = logging.getLogger(__name__)


class Project(object):
    def __init__(self, name=None, dump_dir=None,
                 db_path=None):
        self.name = name or time.strftime("%Y%m%d-%H%M%S")
        self.measurement_results = {}
        self.dump_dir = dump_dir
        self.db_path = db_path
        self.report_name = 'report.html'
        self.dump_name = 'dump.pickle'
        self.plot_folder = 'plots'
        self.template_env = None
        self.prepare_template_env()
        self.measurements = []
        self.parsers = []
        self.filename_replacements = [(r'\s', r''),
                                      (r'\.', r'_'),
                                      (r',', r'_'),
                                      (r'\(', r''),
                                      (r'\)', r'')]

    def _generic_main(self, objects, name_stem, short_name):

        list_name = "{}_list".format(short_name)
        results = "{}_results".format(name_stem)
        store_results = True

        try:
            getattr(self, results)
        except AttributeError:
            log.debug("No {} attribute in Project class. "
                      "Output from {} objects will not be stored."
                      .format(results, name_stem))
            store_results = False

        for obj in objects:
            for sub_obj in obj[list_name]:
                enabled = sub_obj.get('enabled', True)
                if not enabled:
                    continue
                object_name = obj['name']
                if sub_obj['name']:
                    object_name = os.path.join(object_name,
                                               sub_obj['name'])
                log.info("Doing {} {}".format(name_stem, object_name))
                objekt = sub_obj[name_stem]
                cacher = cache_data(cache_key=object_name)
                get_results = cacher(objekt)
                # def get_results():
                #     return objekt()
                try:
                    obj_results = get_results()
                except pickle.PicklingError:
                    obj_results = objekt()
                template_name = sub_obj.get('template_name', None)
                plot_objects = sub_obj.get('plots', None)

                if store_results:
                    getattr(self, results)[object_name] = obj_results

                    if self.dump_dir and obj_results is not None:
                        self.dump_result(object_name, obj_results)

                    if template_name:
                        template = self.get_template(template_name)
                        if plot_objects:
                            plots = plot_objects(obj_results)
                        else:
                            plots = None
                        self.write_report(template, object_name,
                                          time.strftime("%c"), obj_results, plots)

    def main(self):
        log.debug("Running Project: {}".format(self.name))
        self.populate_measurements()
        self._generic_main(self.measurements, "measurement", "meas")

    def populatedb(self):
        log.debug("Populating Project Database: {}".format(self.name))
        self.populate_parsers()
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
            enabled = obj.get('enabled', True)
            if not enabled:
                continue
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
                    the_list = ({'name': None, name_stem: o, },)

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
        with open(os.path.join(dump_path, self.dump_name), 'wb') as f:
            try:
                pickle.dump(to_dump, f)
            except pickle.PicklingError:
                pass

    def write_report(self, template, measurement_name, date,
                     measurement_results, plots=None):
        to_report = {}
        try:

            for k, v in measurement_results.items():
                try:
                    vv = v._asdict()  # Convert namedtuple to dict
                except AttributeError:
                    vv = {'result': v}
                vv['hash'] = self.hash_name(k)
                to_report[k] = vv
            report_dir = os.path.join(self.dump_dir, measurement_name)
        except AttributeError:
            log.error("Measurement doesn't return a dict.")
            raise

        if not os.path.exists(report_dir):
            os.makedirs(report_dir)

        plot_files = {}
        if plots:
            for k, v in plots.items():
                file_name = os.path.join(report_dir,
                                         self.plot_folder,
                                         self._sanitize_filename(k)) + '.png'
                self.save_fig(v, file_name)
                plot_files[k] = file_name
            plt.close('all')
        to_report = dict_to_ordered_dict(to_report)  # Sort it
        rendered = self.render_template(template, measurement_name, date,
                                        to_report, plot_files)

        with open(os.path.join(report_dir, self.report_name), 'w') as f:
            f.write(rendered)
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)

    @staticmethod
    def hash_name(result_name):
        result_name = str(result_name)
        hash_object = hashlib.md5(result_name.encode('utf-8'))
        hashed_name = hash_object.hexdigest()
        return hashed_name

    @staticmethod
    def read_result(result_path):
        with open(result_path, 'r') as f:
            result = pickle.load(f)
        return result

    def dumps(self, measurement_name, results):
        to_dump = copy.deepcopy(results)
        to_dump['date'] = time.strftime("%c")
        to_dump['measurement_name'] = measurement_name
        return to_dump

    @staticmethod
    def render_template(template, measurement_name, date, results, plots=None):
        template_dic = {
            'title': measurement_name,
            'measurement_results': results,
            'measurement_date': date,
            'plots': plots,
        }
        rendered = template.render(**template_dic)
        return rendered

    def save_fig(self, fig, filename):
        folder = os.path.dirname(filename)
        if not os.path.exists(folder):
            os.makedirs(folder)
        fig.savefig(filename, format='png')

    def _sanitize_filename(self, key):
        filename = str(key)
        for pattern, repl in self.filename_replacements:
            filename = re.sub(pattern, repl, filename)
        return filename
