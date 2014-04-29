import imp
import simplejson
import os
import logging
import time


class App(object):
    def __init__(self, directory, name=None, dump_dir=None, template=None,
                 db_path=None):
        self.name = name or time.strftime("%Y%m%d-%H%M%S")
        self.registers = {}
        self.module_names = ['sources', 'views', 'models', 'simulations']
        self._populate_registers(directory)
        self.simulation_results = {}
        self.dump_dir = dump_dir
        self.template = template
        self.db_path = db_path
        self.report_name = 'report.html'
        self.dump_name = 'dump.json'

    def _populate_registers(self, directory):
        """
        Populates the registers with anything that used the appropriate
        decorator.
        """
        for mod in self.module_names:
            imp.load_source(mod, os.path.join(directory, mod + '.py'))
        #  Now the modules are loaded and the relevant registers are populated.
        from pyon import registered_sources, registered_views, \
            registered_models, registered_simulations

        self.registers['sources'] = registered_sources
        self.registers['views'] = registered_views
        self.registers['models'] = registered_models
        self.registers['simulations'] = registered_simulations

    def main(self):
        logging.debug("Running App: {}".format(self.name))
        for sim_name, sim in self.registers['simulations'].items():
            logging.info("Doing {}".format(sim_name))
            my_sim = sim()
            sim_results = my_sim.get_results()
            self.simulation_results[sim_name] = sim_results

            if self.dump_dir:
                self.dump_result(sim_name, sim_results)

            if self.template:
                self.write_report(sim_name, sim_results)

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

    def write_report(self, sim_name, sim_results):
        rendered = self.render_template(self.template, sim_name,
                                        sim_results)
        report_dir = os.path.join(self.dump_dir,
                                  self.name + '_' + sim_name)
        if not os.path.exists(report_dir):
            os.mkdir(report_dir)
        with open(os.path.join(report_dir, self.report_name), 'w') as f:
            f.write(rendered)

    def dumps(self, sim_name, results):
        to_dump = self._sanitize_dic(results)
        to_dump['date'] = time.strftime("%c")
        to_dump['sim_name'] = sim_name
        return to_dump

    @staticmethod
    def render_template(template, sim_name, results):
        template_dic = {
            'title': 'Report: ' + sim_name,
            'sim_results': results,
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
