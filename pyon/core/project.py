import hashlib
from django.utils import six
from jinja2 import Environment, FileSystemLoader
import simplejson
import os
import logging
import time
from importlib import import_module
from django.conf import settings


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
        self.populate_measurements()

    def main(self):
        logging.debug("Running Project: {}".format(self.name))
        #logging.debug("measurements: {}".format(self.measurements))
        for meas in self.measurements:
            for sub_meas in meas['meas_list']:
                measurement_name = meas['name']
                if sub_meas['name']:
                    measurement_name = os.path.join(measurement_name,
                                                    sub_meas['name'])
                logging.info("Doing {}".format(measurement_name))
                measurement = sub_meas['measurement']
                meas_results = measurement.run()
                template_name = sub_meas.get('template_name', None)
                #sim_plots = my_sim.get_plots()
                self.measurement_results[measurement_name] = meas_results

                if self.dump_dir:
                    self.dump_result(measurement_name, meas_results)

                if template_name:
                    template = self.get_template(template_name)
                    self.write_report(template, measurement_name,
                                      time.strftime("%c"), meas_results)

    def prepare_template_env(self):
        template_folders = settings.TEMPLATE_DIRS
        self.template_env = Environment(
            loader=FileSystemLoader(template_folders))

    def get_template(self, template_name):
        return self.template_env.get_template(template_name)

    def populate_measurements(self):
        """
        Traverse from the root measurement module and get all the measurements.
        """
        meas_mod = import_module(settings.ROOT_MEASUREMENTS)
        #  Get the attribute `measurements` from the `ROOT_MEASUREMENTS`
        #  module.
        measurements = getattr(meas_mod, 'measurements')
        for meas in measurements:  #  This is an iterable, so iterate over it.
            m = meas['measurement']  # Get the `measurement` value of the dict
            if isinstance(m, six.string_types):
                #  If it's a string, assume it is the name of a module in
                #  another package.
                sub_mod = import_module(m)
                sub_meas_list = getattr(sub_mod, 'measurements')
                meas_dict = {'name': meas['name'], 'meas_list': sub_meas_list}
                self.measurements.append(meas_dict)
            else:
                #  Otherwise, it should be an instance of a Measurement
                meas_dict = {'name': meas['name'],
                             'meas_list': ({'name': None, 'measurement': m,
                                            'template_name': meas['template_name']},)}
                self.measurements.append(meas_dict)

    def dump_result(self, measurement_name, measurement_results):
        dump_path = os.path.join(self.dump_dir, measurement_name)
        if not os.path.exists(dump_path):
            os.makedirs(dump_path)
        logging.info("Dumping results to {}".format(dump_path))
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
                        logging.debug("Sanitize failed for {}".format(key))
                        pass
            else:
                new_dic[key] = dic[key]
        return new_dic
