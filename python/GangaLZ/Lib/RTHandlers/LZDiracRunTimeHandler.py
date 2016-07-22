#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\#
import os
from textwrap import dedent

from Ganga.GPIDev.Adapters.IRuntimeHandler import IRuntimeHandler
from Ganga.GPIDev.Adapters.StandardJobConfig import StandardJobConfig
from Ganga.GPIDev.Lib.File.FileBuffer import FileBuffer
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\#


class LZDiracRunTimeHandler(IRuntimeHandler):

    """The runtime handler to run Gaudi jobs on the Dirac backend"""

    dirac_script_template = dedent(r"""
    # dirac job created by ganga
    from DIRAC.Core.Base.Script import parseCommandLine
    parseCommandLine()
    from DIRAC.Interfaces.API.Dirac import Dirac
    from DIRAC.Interfaces.API.Job import Job
    
    dirac = Dirac()
    j = Job()
    
    j.setName({name!r})
    j.setExecutable({executable!r}, {arguments!r}, {logfile!r})
    j.setInputSandbox({inputsandbox!s})
    {parameters!s}
    
    # submit the job to dirac
    j.setPlatform( 'ANY' )
    result = dirac.submit(j)
    output(result)
    """).lstrip()

    def prepare(self, app, appsubconfig, appmasterconfig, jobmasterconfig):

        macro_name = os.path.basename(app.macro)
        jobname = os.path.splitext(macro_name)[0] + "%(args)s"
        arguments = macro_name + " %(args)s"
        parameters = 'j.setParameterSequence("args", %s, addToWorkflow=True)' \
                     % [str(i) for i in xrange(app.seed, app.seed + app.njobs)]
        dirac_script = LZDiracRunTimeHandler.dirac_script_template.format(name=jobname,
                                                                          executable=appsubconfig.exe.name,
                                                                          arguments=arguments,
                                                                          logfile="LUXSIM_output.log",
                                                                          inputsandbox='##INPUT_SANDBOX##',
                                                                          parameters=parameters)

        return StandardJobConfig(dirac_script, inputbox=appsubconfig.getSandboxFiles(), outputbox=[])
