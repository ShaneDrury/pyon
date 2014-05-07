import hashlib
import imp
import simplejson
import os
import logging
import time


class App(object):
    def __init__(self, directory, name=None, dump_dir=None, template=None,
                 db_path=None):
        self.name = name or time.strftime("%Y%m%d-%H%M%S")
        self.simulation_results = {}
        self.dump_dir = dump_dir
        self.template = template
        self.db_path = db_path
        self.report_name = 'report.html'
        self.dump_name = 'dump.json'
        self.simulations = {}

    # def _populate_registers(self, directory):
    #     """
    #     Populates the registers with anything that used the appropriate
    #     decorator.
    #     """
    #     # for mod in self.module_names:
    #     #     imp.load_source(mod, os.path.join(directory, mod + '.py'))
    #     # #  Now the modules are loaded and the relevant registers
    # are populated.
    #     # from pyon import registered_sources, registered_views, \
    #     #     registered_models, registered_simulations
    #     #
    #     # self.registers['sources'] = registered_sources
    #     # self.registers['views'] = registered_views
    #     # self.registers['models'] = registered_models
    #     # self.registers['simulations'] = registered_simulations

    def register_simulation(self, sim, sim_name):
        if sim_name not in self.simulations:
            self.simulations[sim_name] = sim
        #self.register_to_dict('simulations', sim_name, sim)

    # def register_to_dict(self, register_to, name, f):
    #     dic = getattr(self, register_to)
    #     if name not in dic:
    #         dic[name] = f

    def main(self):
        logging.debug("Running App: {}".format(self.name))
        logging.debug("Simulations: {}".format(self.simulations))
        for sim_name, sim in self.simulations.items():
            logging.info("Doing {}".format(sim_name))
            my_sim = sim()
            sim_results = my_sim.get_results()
            sim_plots = my_sim.get_plots()
            self.simulation_results[sim_name] = sim_results

            if self.dump_dir:
                self.dump_result(sim_name, sim_results)

            if self.template:
                self.write_report(sim_name, time.strftime("%c"), sim_results)

    def dump_result(self, sim_name, sim_results):
        dump_path = os.path.join(self.dump_dir,
                                 self.name
                                 + '_' + sim_name)
        if not os.path.exists(dump_path):
            os.mkdir(dump_path)
        logging.info("Dumping results to {}".format(dump_path))
        to_dump = self.dumps(sim_name, sim_results)
        with open(os.path.join(dump_path, self.dump_name), 'w') as f:
            simplejson.dump(to_dump, f, namedtuple_as_object=True)

    def write_report(self, sim_name, date, sim_results):
        to_report = {}
        for k, v in sim_results.items():
            vv = v._asdict()
            vv['hash'] = self.hash_name(k)
            to_report[k] = vv
        rendered = self.render_template(self.template, sim_name, date,
                                        to_report)
        report_dir = os.path.join(self.dump_dir,
                                  self.name + '_' + sim_name)
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

    def dumps(self, sim_name, results):
        to_dump = self._sanitize_dic(results)
        to_dump['date'] = time.strftime("%c")
        to_dump['sim_name'] = sim_name
        return to_dump

    @staticmethod
    def render_template(template, sim_name, date, results):
        template_dic = {
            'title': sim_name,
            'sim_results': results,
            'sim_date': date,
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
