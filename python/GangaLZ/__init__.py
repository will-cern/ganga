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

