#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\#
import os
from GangaGaudi.Lib.RTHandlers.RunTimeHandlerUtils import script_generator
from GangaDirac.Lib.RTHandlers.DiracRTHUtils import mangle_job_name, diracAPI_script_template, diracAPI_script_settings
from Ganga.GPIDev.Adapters.IRuntimeHandler import IRuntimeHandler
from Ganga.GPIDev.Adapters.StandardJobConfig import StandardJobConfig
from Ganga.Utility.Config import getConfig
from Ganga.Utility.util import unique
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\#


class LZDiracRunTimeHandler(IRuntimeHandler):

    """The runtime handler to run Gaudi jobs on the Dirac backend"""

    def prepare(self, app, appsubconfig, appmasterconfig, jobmasterconfig):

        dirac_script = script_generator(diracAPI_script_template(),
                                        DIRAC_IMPORT='from DIRAC.Interfaces.API.Dirac import Dirac',
                                        DIRAC_JOB_IMPORT='from DIRAC.Interfaces.API.Job import Job',
                                        DIRAC_OBJECT='Dirac()',
                                        JOB_OBJECT='Job()',
                                        NAME=mangle_job_name(app),
                                        EXE=appsubconfig.exe,
                                        EXE_LOG_FILE='Ganga_output.log',
                                        OUTPUT_SANDBOX=appsubconfig.outputbox,
                                        OUTPUT_SE=getConfig(
                                            'DIRAC')['DiracOutputDataSE'],
                                        INPUT_SANDBOX=appsubconfig.inputbox
                                        )

        return StandardJobConfig(dirac_script,
                                 inputbox=appsubconfig.inputbox,
                                 outputbox=appsubconfig.outputbox)
