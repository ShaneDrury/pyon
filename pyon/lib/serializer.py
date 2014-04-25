import json
from pyon.lib.register import Register

registered_serializers = {}


class Serializer(object):
    def dump(self):
        pass

    def dumps(self):
        pass

    def load(self):
        pass

    def loads(self):
        pass


@Register(registered_serializers, 'json')
class JSONSerializer(Serializer):
    def dump(self, *args, **kwargs):
        json.dump(*args, **kwargs)

    def dumps(self, *args, **kwargs):
        json.dumps(*args, **kwargs)

    def load(self, *args, **kwargs):
        json.load(*args, **kwargs)

    def loads(self, *args, **kwargs):
        json.loads(*args, **kwargs)


@Register(registered_serializers, 'string')
class StringSerializer(Serializer):
    """
    Just return a string.
    """
    def dumps(self, *args):
        return args[0]