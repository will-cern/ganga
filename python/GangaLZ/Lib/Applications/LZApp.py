##########################################################################
# Ganga Project. http://cern.ch/ganga
#
# $Id: IApplication.py,v 1.1 2008-07-17 16:40:52 moscicki Exp $
##########################################################################

from Ganga.GPIDev.Adapters.IPrepareApp import IPrepareApp
from Ganga.GPIDev.Schema import Schema, Version, SimpleItem


from Ganga.Utility.Config import getConfig
from Ganga.Utility.files import expandfilename

config = getConfig("Preparable")

class LZApp(IPrepareApp):

    """
    Base class for all applications which can be placed into a prepared\
    state. 
    """
    _schema = Schema(Version(0, 0), {
        'luxsim_version': SimpleItem(defvalue=None, typelist=[None, str]),
        'g4_version':SimpleItem(defvalue=None, typelist=[None, str]),
        'LZSim2AnalysisTree_version':SimpleItem(defvalue=None, typelist=[None, str]),
        'libnest_version': SimpleItem(defvalue=None, typelist=[None, str]),
    })
    _category = 'applications'

    def __init__(self):
        super(IPrepareApp, self).__init__()


    def configure(self, master_appconfig):
        pass

    def prepare(self, force=False):
        """
        Base class for all applications which can be placed into a prepared\
        state. 

        """
        pass

