##########################################################################
# Ganga Project. http://cern.ch/ganga
#
# $Id: IApplication.py,v 1.1 2008-07-17 16:40:52 moscicki Exp $
##########################################################################

from Ganga.GPIDev.Adapters.IApplication import IApplication
from Ganga.GPIDev.Adapters.StandardJobConfig import StandardJobConfig
from Ganga.GPIDev.Schema import Schema, Version, SimpleItem
import textwrap
import os
import logging
from Ganga.Utility.Config import getConfig
from Ganga.Utility.files import expandfilename
logger = logging.getLogger(__name__)

config = getConfig("Preparable")

class LZApp(IApplication):

    """
    Base class for all applications which can be placed into a prepared\
    state. 
    """
    _schema = Schema(Version(0, 0), {
        'luxsim_version': SimpleItem(defvalue='3.7.0', typelist=[str]),
        'g4_version':SimpleItem(defvalue='4.9.5.p02', typelist=[str]),
        'libnest_version': SimpleItem(defvalue='2.11.0', typelist=[str]),
        'reduction_version':SimpleItem(defvalue='3.10.0', typelist=[str]),
    })
    _category = 'applications'

    def __init__(self):
        super(IApplication, self).__init__()

    def run_script(self):
        return textwrap.dedent(r"""
        #!/bin/bash
        #Prepare some variables based on the inputs
        MACRO_FILE=$1
        export SEED=$2 # an integer that will label the output file
        LUXSIM_DIR=/cvmfs/lz.opensciencegrid.org/LUXSim/release-###LUXSIM_VERSION###/
        ROOT_DIR=/cvmfs/lz.opensciencegrid.org/ROOT/v5.34.32/slc6_gcc44_x86_64/root/
        G4_DIR=/cvmfs/lz.opensciencegrid.org/geant4/
        G4VER=geant###G4_VERSION###
        LIBNEST_DIR=/cvmfs/lz.opensciencegrid.org/fastNEST/
        LIBNEST_VERSION=###LIBNEST_VERSION###
        DATA_STORE_PATH=/lz/data
        DATA_STORE_SE=UKI-LT2-IC-HEP-disk
        BIGROOT_STORE_PATH=$DATA_STORE_PATH/LUXSim_$(basename $LUXSIM_DIR)_$G4VER/$(basename $MACRO_FILE _parametric.mac)

        REDUCTION_VERSION=###REDUCTION_VERSION###
        REDUCTION_LABEL=reduced_v$REDUCTION_VERSION
        CONVERTER_EXE=/cvmfs/lz.opensciencegrid.org/TDRAnalysis/release-$REDUCTION_VERSION/ReducedAnalysisTree/LZSim2AnalysisTree
        REDUCED_STORE_PATH=$DATA_STORE_PATH/LUXSim_$(basename $LUXSIM_DIR)_$G4VER/$REDUCTION_LABEL/$(basename $MACRO_FILE _parametric.mac)


        export OUTPUT_DIR=$(pwd)
        #extract the name of the output file from the LUXSim macro
        OUTPUT_FILE=$(awk '/^\/LUXSim\/io\/outputName/ {print $2}' $1 | tail -1)$2.bin


        # move into the LUXSim directory, set G4 env, and run the macro
        cd $LUXSIM_DIR
        source $G4_DIR/etc/geant4env.sh $G4VER
        $LUXSIM_DIR/LUXSimExecutable $OUTPUT_DIR/$MACRO_FILE

        # after macro has run, rootify
        cd $OUTPUT_DIR
        source $ROOT_DIR/bin/thisroot.sh
        $LUXSIM_DIR/tools/LUXRootReader $OUTPUT_FILE
        OUTPUT_ROOT_FILE=$(basename $OUTPUT_FILE .bin).root

        # reduce and then copy both to our central storage.

        source $LIBNEST_DIR/release-$LIBNEST_VERSION/libNEST/thislibNEST.sh
        OUTPUT_REDUCED_FILE=${OUTPUT_ROOT_FILE/".root"/"_analysis_tree.root"}
        $CONVERTER_EXE $OUTPUT_DIR/$OUTPUT_ROOT_FILE $OUTPUT_DIR/$OUTPUT_REDUCED_FILE

        dirac-dms-add-file $BIGROOT_STORE_PATH/$OUTPUT_ROOT_FILE $OUTPUT_DIR/$OUTPUT_ROOT_FILE $DATA_STORE_SE
        dirac-dms-add-file $REDUCED_STORE_PATH/$OUTPUT_REDUCED_FILE $OUTPUT_DIR/$OUTPUT_REDUCED_FILE $DATA_STORE_SE
        """).replace('###LUXSIM_VERSION###', self.luxsim_version)\
            .replace('###G4_VERSION###', self.g4_version)\
            .replace('###LIBNEST_VERSION###', self.libnest_version)\
            .replace('###REDUCTION_VERSION###', self.reduction_version)

    def configure(self, master_appconfig):
        input_workspace = self.getJobObject().getInputWorkspace().getPath()
        run_script = os.path.join(input_workspace, 'runLUXSim_parametric.sh')
        with open(run_script, 'wb') as f:
            f.write(self.run_script())
        return (None, StandardJobConfig(exe=run_script))

#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\#

# Associate the correct run-time handlers LZApp

from Ganga.GPIDev.Adapters.ApplicationRuntimeHandlers import allHandlers
from GangaLZ.Lib.RTHandlers.LZDiracRunTimeHandler import LZDiracRunTimeHandler

allHandlers.add('LZApp', 'Local', LZDiracRunTimeHandler)
allHandlers.add('LZApp', 'Dirac', LZDiracRunTimeHandler)

#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\#


