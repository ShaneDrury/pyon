import hashlib
import simplejson
import os
import logging
import time
from importlib import import_module


class Project(object):
    def __init__(self, name=None, dump_dir=None,
                 db_path=None):
        self.name = name or time.strftime("%Y%m%d-%H%M%S")
        self.measurement_results = {}
        self.dump_dir = dump_dir
        self.db_path = db_path
        self.report_name = 'report.html'
        self.dump_name = 'dump.json'
        self.measurements = {}

    def register_measurement(self, measurement):
        mod_path, _, meas_name = measurement.rpartition('.')
        mod = import_module(mod_path)
        meas_func = getattr(mod, meas_name)
        template = getattr(mod, 'template')

        if meas_name not in self.measurements:
            self.measurements[meas_name] = {'f': meas_func,
                                            'template': template}

    def main(self):
        logging.debug("Running Project: {}".format(self.name))
        logging.debug("measurements: {}".format(self.measurements))
        for measurement_name, meas in self.measurements.items():
            logging.info("Doing {}".format(measurement_name))
            measurement_results = meas['f']()
            template = meas['template']
            #sim_plots = my_sim.get_plots()
            self.measurement_results[measurement_name] = measurement_results

            if self.dump_dir:
                self.dump_result(measurement_name, measurement_results)

            if template:
                self.write_report(template, measurement_name,
                                  time.strftime("%c"), measurement_results)

    def dump_result(self, measurement_name, measurement_results):
        dump_path = os.path.join(self.dump_dir, measurement_name)
        if not os.path.exists(dump_path):
            os.mkdir(dump_path)
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
            os.mkdir(report_dir)
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
