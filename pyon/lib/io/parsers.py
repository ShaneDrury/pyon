from itertools import chain
from pyon.lib.io.folder import get_list_of_files
from pyon.lib.io.formats import parse_iwasaki_32c_charged_meson_file
from pyon.lib.register import Register

__author__ = 'srd1g10'
"""
Thoughts about parsing. A base class called FileParser is probably going to be useful.
We want to customise this as an object through things like fp.parser = ... (see formats.py for examples).
The file formats vary wildly. With one output file, there may be many mass/charge combinations or there may be many
config_numbers in one file. To cope with this, the FileParser needs to be as flexible as possible. An idea is that it
could just parse all the data in the file and return it all. Then it is left up to the user to filter this by the data
they want. This would keep the parsing functions relatively simple. In other words a parser's function is separated
from giving us the data we actually want. A parser's role is just to return all the data possible from the file.
Filtering the data can be implemented in helper functions in io/filtering.py.

Is a FileParser class needed? All we really need is something like parse_wme_file(file_name), which is better as a
function.
The file parsers.py should then contain common logic for each of the formats e.g. scientific regex and the ingredients
needed to parse a particular format. formats.py brings these together without cluttering up the module.

===

Similar to Django, it's nice to have things like raw_data.filter(source=GAM_5, ...)
For this, we need a class Data
"""
registered_parsers = {}


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


@Register(registered_parsers, 'iwasaki_32c')
class Iwasaki32c(Parser):
    def get_from_file(self, file_name):
        return parse_iwasaki_32c_charged_meson_file(file_name)


