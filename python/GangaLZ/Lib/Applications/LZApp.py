##########################################################################
# Ganga Project. http://cern.ch/ganga
#
# $Id: IApplication.py,v 1.1 2008-07-17 16:40:52 moscicki Exp $
##########################################################################
import os
import string
import logging
from textwrap import dedent
from git import Git

from Ganga.GPIDev.Adapters.IApplication import IApplication
from Ganga.GPIDev.Adapters.StandardJobConfig import StandardJobConfig
from Ganga.GPIDev.Schema import Schema, Version, SimpleItem
from Ganga.GPIDev.Lib.File.FileBuffer import FileBuffer
from Ganga.Utility.Config import getConfig

logger = logging.getLogger(__name__)
config = getConfig('Configuration')

with open(os.path.join(os.path.dirname(__file__),
                       'LZ_ApplicationScript_template.sh'), 'r') as file_:
    runscript_template = string.Template(file_.read())
macro_extras = string.Template(dedent("""
    /control/getEnv SEED
    /$app/randomSeed {SEED}
    /$app/beamOn $nevents
    exit
    """))

macro_app_map = {'LUXSim': 'LUXSim',
                 'BACCARAT': 'Bacc'}

class LZApp(IApplication):

    """
    Base class for all applications which can be placed into a prepared\
    state. 
    """
    _schema = Schema(Version(0, 0), {
        'app': SimpleItem(defvalue='LUXSim', typelist=[basestring]),
        'app_version': SimpleItem(defvalue='3.7.0', typelist=[basestring]),
        'g4_version':SimpleItem(defvalue='4.9.5.p02', typelist=[basestring]),
        'root_version': SimpleItem(defvalue='5.34.32', typelist=[basestring]),
        'root_arch': SimpleItem(defvalue='slc6_gcc44_x86_64', typelist=[basestring]),
        'libnest_version': SimpleItem(defvalue='3.0.2', typelist=[basestring]),
        'reduction_version':SimpleItem(defvalue='3.15.0', typelist=[basestring]),
        'tag':SimpleItem(defvalue='2.0.0', typelist=[basestring]),
        'macro':SimpleItem(defvalue='/home/hep/arichard/git/ganga/macroTemplate.mac', typelist=[basestring]),
        'njobs':SimpleItem(defvalue=3, typelist=[int]),
        'nevents':SimpleItem(defvalue=100000, typelist=[int]),
        'seed':SimpleItem(defvalue=9000000, typelist=[int]),
        'requestid':SimpleItem(defvalue='None', typelist=[basestring]),
    })
    _category = 'applications'

    def configure(self, master_appconfig):
        run_script = FileBuffer('run%s_parametric.sh' % self.app,
                                runscript_template.safe_substitute(app=self.app,
                                                                   app_version=self.app_version,
                                                                   root_version=self.root_version,
                                                                   root_arch=self.root_arch,
                                                                   g4_version=self.g4_version,
                                                                   libnest_version=self.libnest_version,
                                                                   reduction_version=self.reduction_version),
                                executable=True)
        


        git_dir = os.path.join(config['gangadir'], 'LZGit', 'TDRAnalysis')
        if not os.path.isdir(git_dir):
            Git().clone('git@lz-git.ua.edu:sim/TDRAnalysis.git', git_dir)
        else:
            Git(git_dir).fetch('origin')

        Git(git_dir).checkout(self.tag)
        logger.info("Using git dir %s and macro %s", git_dir, self.macro)
        
        macro = os.path.join(git_dir, self.macro)
        if not os.path.isfile(macro):
            logger.error("Macro file '%s' doesn't exist", macro)
            return (None, StandardJobConfig(exe=run_script))
        with open(macro, 'rb') as m:
            macro_buffer = FileBuffer(os.path.basename(macro), m)
            macro_buffer += macro_extras.safe_substitute(app=macro_app_map.get(self.app),
                                                         nevents=self.nevents)

        return (None, StandardJobConfig(exe=run_script, inputbox=[macro_buffer]))

#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\#

# Associate the correct run-time handlers LZApp

from Ganga.GPIDev.Adapters.ApplicationRuntimeHandlers import allHandlers
from GangaLZ.Lib.RTHandlers.LZDiracRunTimeHandler import LZDiracRunTimeHandler

allHandlers.add('LZApp', 'LZDirac', LZDiracRunTimeHandler)

#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\#


