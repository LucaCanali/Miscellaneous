# An example of how to convert ROOT files into Apache Parquet using uproot

# download root files, for example
# get xrootd tools:
# https://xrootd.slac.stanford.edu/
#
# download/copy locally. example:
xrdcp root://eospublic.cern.ch//eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/Run2012BC_DoubleMuParked_Muons.root .

####
use uproot and awkward array to convert it

# this requires
# pip install uproot
# pip install awkward

------
import uproot
import awkward as ak

input_name = "Run2012BC_DoubleMuParked_Muons.root"
output_name = "Run2012BC_DoubleMuParked_Muon.parquet"

f = uproot.open(input_name)

# find the keys in the file
#f.classnames()
f.keys()

#ttree = f["PhaseSpaceTree"]
ttree = f[f.keys()[0].split(';')[0]]

# use awkward arrays to load data and save in Apache Parquet format

ak.to_parquet(ttree.arrays(), output_name)
