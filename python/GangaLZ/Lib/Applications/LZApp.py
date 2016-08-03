##########################################################################
# Ganga Project. http://cern.ch/ganga
#
# $Id: IApplication.py,v 1.1 2008-07-17 16:40:52 moscicki Exp $
##########################################################################
import os
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

class LZApp(IApplication):

    """
    Base class for all applications which can be placed into a prepared\
    state. 
    """
    _schema = Schema(Version(0, 0), {
        'luxsim_version': SimpleItem(defvalue='3.7.0', typelist=[basestring]),
        'g4_version':SimpleItem(defvalue='4.9.5.p02', typelist=[str]),
        'libnest_version': SimpleItem(defvalue='2.11.0', typelist=[str]),
        'reduction_version':SimpleItem(defvalue='3.10.0', typelist=[basestring]),
        'tag':SimpleItem(defvalue='2.0.0', typelist=[basestring]),
        'macro':SimpleItem(defvalue='/home/hep/arichard/git/ganga/macroTemplate.mac', typelist=[basestring]),
        'njobs':SimpleItem(defvalue=3, typelist=[int]),
        'nevents':SimpleItem(defvalue=100000, typelist=[int]),
        'seed':SimpleItem(defvalue=9000000, typelist=[int]),
    })
    _category = 'applications'

    runscript = dedent(r"""    
    #!/bin/bash
    #Prepare some variables based on the inputs
    MACRO_FILE=$1
    export SEED=$2 # an integer that will label the output file
    LUXSIM_DIR=/cvmfs/lz.opensciencegrid.org/LUXSim/release-{luxsim_version!s}/
    ROOT_DIR=/cvmfs/lz.opensciencegrid.org/ROOT/v5.34.32/slc6_gcc44_x86_64/root/
    G4_DIR=/cvmfs/lz.opensciencegrid.org/geant4/
    G4VER=geant{g4_version!s}
    LIBNEST_DIR=/cvmfs/lz.opensciencegrid.org/fastNEST/
    LIBNEST_VERSION={libnest_version!s}
    DATA_STORE_PATH=/lz/data
    DATA_STORE_SE=UKI-LT2-IC-HEP-disk
    BIGROOT_STORE_PATH=$DATA_STORE_PATH/LUXSim_$(basename $LUXSIM_DIR)_$G4VER/$(basename $MACRO_FILE _parametric.mac)
    
    REDUCTION_VERSION={reduction_version!s}
    REDUCTION_LABEL=reduced_v$REDUCTION_VERSION
    CONVERTER_EXE=/cvmfs/lz.opensciencegrid.org/TDRAnalysis/release-$REDUCTION_VERSION/ReducedAnalysisTree/LZSim2AnalysisTree
    REDUCED_STORE_PATH=$DATA_STORE_PATH/LUXSim_$(basename $LUXSIM_DIR)_$G4VER/$REDUCTION_LABEL/$(basename $MACRO_FILE _parametric.mac)
    
    
    export OUTPUT_DIR=$(pwd)
    #extract the name of the output file from the LUXSim macro
    OUTPUT_FILE=$(awk '/^\/LUXSim\/io\/outputName/ {{print $2}}' $1 | tail -1)$2.bin
    
    
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
    OUTPUT_REDUCED_FILE=${{OUTPUT_ROOT_FILE/".root"/"_analysis_tree.root"}}
    $CONVERTER_EXE $OUTPUT_DIR/$OUTPUT_ROOT_FILE $OUTPUT_DIR/$OUTPUT_REDUCED_FILE
    
    dirac-dms-add-file $BIGROOT_STORE_PATH/$OUTPUT_ROOT_FILE $OUTPUT_DIR/$OUTPUT_ROOT_FILE $DATA_STORE_SE
    dirac-dms-add-file $REDUCED_STORE_PATH/$OUTPUT_REDUCED_FILE $OUTPUT_DIR/$OUTPUT_REDUCED_FILE $DATA_STORE_SE
    """).lstrip()

    def configure(self, master_appconfig):
        run_script = FileBuffer('runLUXSim_parametric.sh',
                                LZApp.runscript.format(luxsim_version=self.luxsim_version,
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
        logger.warning("Using git dir %s and macro %s", git_dir, self.macro)
        
        macro = os.path.join(git_dir, self.macro)
        if not os.path.isfile(macro):
            logger.warn("Macro file '%s' doesn't exist", macro)
        with open(macro, 'rb') as m:
            macro_buffer = FileBuffer(os.path.basename(macro), m)
            macro_buffer += dedent("""
            /control/getEnv SEED
            /LUXSim/randomSeed {SEED}
            /LUXSim/beamOn %s
            exit
            """ % self.nevents)

        return (None, StandardJobConfig(exe=run_script, inputbox=[macro_buffer]))

#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\#

# Associate the correct run-time handlers LZApp

from Ganga.GPIDev.Adapters.ApplicationRuntimeHandlers import allHandlers
from GangaLZ.Lib.RTHandlers.LZDiracRunTimeHandler import LZDiracRunTimeHandler

allHandlers.add('LZApp', 'Dirac', LZDiracRunTimeHandler)

#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\#


