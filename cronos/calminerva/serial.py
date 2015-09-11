"""
calminerva.serial
-----------------

JSON serialization/deserialization for `calminerva.models`.
"""
import datetime
import dateutil.parser
import json

from . import models


def _recurse_asdict(data):
    try:
        return data._asdict()
    except AttributeError:
        try:
            return {k: _recurse_asdict(v) for k, v in data.items()}
        except AttributeError:
            if isinstance(data, list):
                return [_recurse_asdict(elem) for elem in data]
            else:
                return data


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        else:
            return super().default(obj)


def dump(items, **kwargs):
    """
    Export item to JSON.

    Parameters
    ----------
    items : list
        items can be either `Course`s or `Event`s.
    kwargs
        Passed to `json.dumps`.
    """
    data = _recurse_asdict(items)
    return json.dumps(data, cls=Encoder, **kwargs)


def pretty_dump(items):
    return dump(items, indent=4, separators=(',', ': '))


class Decoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        # type_key = '__type__'
        # if obj.get(type_key, '') not in models.MODELS:
        #     return super().decode(obj)
        # type_ = obj.pop(type_key)
        # ntuple = getattr(models, type_)
        for date_field in models.date_fields:
            if date_field in obj:
                obj[date_field] = dateutil.parser.parse(obj[date_field])
        return obj


def load(data):
    return json.loads(data, cls=Decoder)


def load_models(items, model, _load=True):
    """
    Deserialize `items` into a given `model`.

    Parameters
    ----------
    items : str or dict
        Can be a list or a single element.
    model : namedtuple from `calminerva.model`
    _load : bool
        If False, `items` is not deserialized.
    """
    if _load:
        items = load(items)
    try:
        return model(**items)
    except TypeError:
        return [model(**x) for x in items]
