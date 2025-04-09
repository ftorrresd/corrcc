# CorrCC

Correctionlib JSON to C compiler.

## Setup

```bash
source setup.sh
```
rm -rf corrections/*.h &&  clear ; clear ; python corrcc.py /cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/JME/2023_Summer23/jet_jerc.json.gz --corrections Summer23Prompt23_RunCv4_JRV1_MC_ScaleFactor_AK4PFPuppi && bat corrections/Summer23Prompt23_RunCv4_JRV1_MC_ScaleFactor_AK4PFPuppi.h
rm -rf corrections/*.h &&  clear ; clear ; ./corrcc /cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/JME/2023_Summer23/jet_jerc.json.gz --corrections Summer23Prompt23_RunCv4_JRV1_MC_ScaleFactor_AK4PFPuppi && bat corrections/Summer23Prompt23_RunCv4_JRV1_MC_ScaleFactor_AK4PFPuppi.h
rm -rf corrections/*.h &&  clear ; clear ; ./corrcc /cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/JME/2023_Summer23/jet_jerc.json.gz --corrections Summer23Prompt23_RunCv4_JRV1_MC_ScaleFactor_AK4PFPuppi && bat corrections/Summer23Prompt23_RunCv4_JRV1_MC_ScaleFactor_AK4PFPuppi.h
rm -rf corrections/*.h &&  clear ; clear ; ./corrcc /cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/JME/2023_Summer23/jet_jerc.json.gz --corrections Summer23Prompt23_RunCv4_JRV1_MC_ScaleFactor_AK4PFPuppi && bat corrections/Summer23Prompt23_RunCv4_JRV1_MC_ScaleFactor_AK4PFPuppi.h
