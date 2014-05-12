from itertools import chain
from pyon.lib.io.folder import get_list_of_files


class Parser(object):
    def get_from_file(self, file_name):
        raise NotImplementedError("Implement this in a derived class.")

    def get_from_files(self, list_of_files):
        raw_data = []
        for ff in list_of_files:
                with open(ff, 'r') as f:
                    raw_data.append(self.get_from_file(f))
        to_return = chain.from_iterable(raw_data)
        return to_return

    def get_from_folder(self, folder):
        return self.get_from_files(get_list_of_files(folder))


