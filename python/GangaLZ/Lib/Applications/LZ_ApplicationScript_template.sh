#!/bin/bash
#Prepare some variables based on the inputs
MACRO_FILE=$1
export SEED=$2 # an integer that will label the output file
APP_DIR=/cvmfs/lz.opensciencegrid.org/$app/release-$app_version/
ROOT_DIR=/cvmfs/lz.opensciencegrid.org/ROOT/v$root_version/$root_arch/root/
G4_DIR=/cvmfs/lz.opensciencegrid.org/geant4/
G4VER=geant$g4_version
LIBNEST_DIR=/cvmfs/lz.opensciencegrid.org/fastNEST/release-$libnest_version/libNEST
DATA_STORE_PATH=/lz/data
DATA_STORE_SE=UKI-LT2-IC-HEP-disk
BIGROOT_STORE_PATH=$DATA_STORE_PATH/${app}_$(basename $APP_DIR)_$G4VER/$(basename $MACRO_FILE _parametric.mac)

REDUCTION_LABEL=reduced_v$reduction_version
CONVERTER_EXE=/cvmfs/lz.opensciencegrid.org/TDRAnalysis/release-$reduction_version/ReducedAnalysisTree/LZSim2AnalysisTree
REDUCED_STORE_PATH=$DATA_STORE_PATH/${app}_$(basename $APP_DIR)_$G4VER/$REDUCTION_LABEL/$(basename $MACRO_FILE _parametric.mac)


export OUTPUT_DIR=$(pwd)
#extract the name of the output file from the LUXSim macro
OUTPUT_FILE=$(awk '/^\/$app\/io\/outputName/ {print $2}' $1 | tail -1)$2.bin


# move into the LUXSim directory, set G4 env, and run the macro
cd $APP_DIR
source $G4_DIR/etc/geant4env.sh $G4VER
$APP_DIR/${app}Executable $OUTPUT_DIR/$MACRO_FILE

# after macro has run, rootify
cd $OUTPUT_DIR
source $ROOT_DIR/bin/thisroot.sh
$APP_DIR/tools/LUXRootReader $OUTPUT_FILE
OUTPUT_ROOT_FILE=$(basename $OUTPUT_FILE .bin).root

# reduce and then copy both to our central storage.

source $LIBNEST_DIR/thislibNEST.sh
OUTPUT_REDUCED_FILE=${OUTPUT_ROOT_FILE/".root"/"_analysis_tree.root"}
$CONVERTER_EXE $OUTPUT_DIR/$OUTPUT_ROOT_FILE $OUTPUT_DIR/$OUTPUT_REDUCED_FILE

#dirac-dms-add-file $BIGROOT_STORE_PATH/$OUTPUT_ROOT_FILE $OUTPUT_DIR/$OUTPUT_ROOT_FILE $DATA_STORE_SE
#dirac-dms-add-file $REDUCED_STORE_PATH/$OUTPUT_REDUCED_FILE $OUTPUT_DIR/$OUTPUT_REDUCED_FILE $DATA_STORE_SE

