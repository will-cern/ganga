from Ganga.Utility.logging import getLogger
logger = getLogger()

def getEnvironment(config=None):
    import sys
    import os.path
    import PACKAGE

    PACKAGE.standardSetup()
    return


def loadPlugins(config=None):
    logger.debug("Loading LZ Applications")
    import Lib.Applications
    import Lib.RTHandlers
    import Lib.Tasks
    import Lib.Backends
    import Lib.PostProcessors
    from Ganga.Core.GangaRepository import addRegistry
##    from Ganga.GPIDev.Lib.Registry import JobRegistry
##    addRegistry(JobRegistry('frank', "FRANK THINGS"))
#    from Ganga.Utility.Config import getConfig
#    display = getConfig('Display')
#    # add display default values for the box
#    display.addOption('f_columns',
#                      ("id", "type", "name", "application"),
#                      'list of job attributes to be printed in separate columns')
#
#    display.addOption('f_columns_width',
#                      {'id': 5, 'type': 20, 'name': 40, 'application': 15},
#                      'width of each column')
#
#    display.addOption('f_columns_functions',
#                      {'application': "lambda obj: obj.application._name"},
#                      'optional converter functions')
#
#    display.addOption('f_columns_show_empty',
#                      ['id'],
#                      'with exception of columns mentioned here, hide all values which evaluate to logical false (so 0,"",[],...)')
#    from Ganga.Core.GangaRepository.Registry import Registry
    from Ganga.GPIDev.Lib.Tasks.TaskRegistry import TaskRegistry
#    from Ganga.GPIDev.Lib.Registry.RegistrySlice import RegistrySlice
#    from Ganga.GPIDev.Lib.Registry.RegistrySliceProxy import RegistrySliceProxy
    r = type('LZTaskRegistry', (TaskRegistry,),{})('lztasks', "LZ Tasks Registry.")
#    r = Registry('frank', "FRANK THINGS")
##    r.stored_slice = RegistrySlice(r.name, 'f')
##    r.stored_proxy = RegistrySliceProxy(r.stored_slice)
#    s = RegistrySlice(r.name, 'f')
#    p = RegistrySliceProxy(s)
#    r.getSlice = lambda: s
#    r.getProxy = lambda: p
    addRegistry(r)
