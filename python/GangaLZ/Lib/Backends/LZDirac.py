from GangaDirac.Lib.Backends.DiracBase import DiracBase
from GangaDirac.Lib.Utilities.DiracUtilities import execute

class LZDirac(DiracBase):

    _name = 'LZDirac'
    _category = 'backends'
    _schema = DiracBase._schema.inherit_copy()
    _exportmethods = DiracBase._exportmethods[:]
    _packed_input_sandbox = DiracBase._packed_input_sandbox
    __doc__ = DiracBase.__doc__
    def _resubmit(self):
        result = execute(r"""output = reschedule(%s)""" % self.id)
