## An example of how to convert ROOT files into Apache Parquet using the Pytho9n package uproot

- Prerequisite: download/copy the root the files to be converted
- For files shared via the XRootD protocol (i.e. URLs like `root://...`)
  - get xrootd tools from https://xrootd.slac.stanford.edu/
  - download/copy locally, for example:
     `xrdcp root://eospublic.cern.ch//eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/Run2012BC_DoubleMuParked_Muons.root .`

## Use uproot and awkward array to read and convert files in ROOT format

- Install 
```
pip install uproot
pip install awkward
```

- From Python:

```
import uproot
import awkward as ak

input_name = "Run2012BC_DoubleMuParked_Muons.root"
output_name = "Run2012BC_DoubleMuParked_Muon.parquet"

f = uproot.open(input_name)

# find the keys in the file
#f.classnames()
f.keys()

#ttree = f["Events"]
ttree = f[f.keys()[0].split(';')[0]]

# use awkward arrays to load data and save in Apache Parquet format

ak.to_parquet(ttree.arrays(), output_name)
```

### How to convert multiple files in a directory

```
import uproot
import awkward as ak
import glob

path = "./"
root_files = glob.glob(path + "*.root")

for name in root_files:
  f = uproot.open(name)
  ttree = f[f.keys()[0].split(';')[0]]
  ak.to_parquet(ttree.arrays(), path + name + ".parquet")
```

### Parquet output tuning 
There are several options available when writing Parquet files, follow the 
[link to awkward arrays documentation](https://awkward-array.org/doc/main/reference/generated/ak.to_parquet.html)
