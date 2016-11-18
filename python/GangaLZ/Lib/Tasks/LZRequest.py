from types import NoneType
from Ganga.GPIDev.Lib.Tasks import ITask
from Ganga.GPIDev.Schema import Schema, Version, SimpleItem

########################################################################


class LZRequest(ITask):

    """LZ Request Task"""
    _schema = Schema(Version(1, 0), dict(ITask._schema.datadict.items() + {
        'requestdb_id': SimpleItem(defvalue=None, typelist=[int, NoneType]),
        'requestdb_status': SimpleItem(defvalue='None', typelist=[basestring])
    }.items()))

    _category = 'tasks'
    _name = 'LZRequest'
    _exportmethods = ITask._exportmethods + []

    _tasktype = "ITask"

    default_registry = "tasks"
