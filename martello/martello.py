
"""
    A class for the Martello predictive model.

    ...

    Attributes
    ----------
    fileLabel: int
        Label of scanned file
    fileProba : float
        Probability of maliciousness of scanned file

    Methods
    -------
    scanfile():
        scans file

    Usage:
    -------
    >>> import martello
    >>> m = martello.PredictiveModel()
    >>> m.scanfile("000b4c3425969471ac872c7e0a230ff7")
    >>> m.fileProba
    0.01
    >>> m.fileLabel
    'Benign'
    >>> model.scanfile("000b4c3425969471ac872c7e0a230ff7",0.6)
    >>> model.fileProba
    0.01
    >>> model.fileLabel
    'Benign'
    

    CLI Usage (with or without prescribed probability threshold for labelling)
    ----------
    $ python martello 000b4c3425969471ac872c7e0a230ff7 0.6
    $ cat *.csv 
       idx                          filename  filesize  nz_features  prob  label
    0    0  000b4c3425969471ac872c7e0a230ff7   1336832         1694  0.01   "Benign"
    $ python martello 000b4c3425969471ac872c7e0a230ff7
    $ cat *.csv 
       idx                          filename  filesize  nz_features  prob  label
    0    0  000b4c3425969471ac872c7e0a230ff7   1336832         1694  0.01   "Benign"
"""


import os, pickle, sys, glob, warnings
import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix
from pathlib import Path

warnings.filterwarnings("ignore", category=DeprecationWarning)

class PredictiveModel:
    def __init__(self,modelpath = Path(__file__).parent.absolute().joinpath("bin"), out_path = ""):
        self.modelpath  = modelpath
        self.classifier = pickle.load(open(self.modelpath/"martello-classifier.pkl", 'rb'))
        self.vectorizer = self.modelpath/"martello-vectorizer-coo"
        self.outfile    = out_path + 'out' + str(os.getpid()) 
        self.topk_file  = self.modelpath/"martello-features.bin"
        self.K = np.fromfile(open(self.topk_file), dtype=np.intc, count=1)[0]
        self.N = 2500
    def scanfile(self,file_, probability_threshold = 0.5):
        [os.remove(file_) for file_ in glob.glob(self.outfile + '*'  , recursive=False)]
        self.fileProba  = None
        self.fileLabel  = None
        status = os.system('export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:%s; \
           %s -f %s -k %s -n 6 -x 6 -t 1 -o %s' \
           %(self.modelpath, self.vectorizer, file_, self.topk_file, self.outfile))
        if status != 0:
            return
        dtm_coo = np.fromfile(self.outfile + '.coo.bin.part0', dtype=np.intc)
        if dtm_coo.size != 0: # check if the scanned file contains features
            dtm_coo = dtm_coo.reshape(-1,3)
            X_csr   = coo_matrix((dtm_coo[:,2], (dtm_coo[:,0], dtm_coo[:,1])), shape=(dtm_coo[-1,0] + 1, self.K)).tocsr()[:,0:self.N]
            self.fileProba = self.classifier.predict_proba(X_csr)[0,1]
            self.fileLabel = "Benign"  if self.fileProba <= float(probability_threshold) else "Malware"
        else:
            print("Scanned file does not contain Martello features")
        if __name__ == "__main__":
            [os.remove(file_) for file_ in glob.glob(self.outfile + '*.bin.part0', recursive=False)]
        else:
            [os.remove(file_) for file_ in glob.glob(self.outfile + '*.part0', recursive=False)]
        [os.remove(file_) for file_ in glob.glob(self.outfile + '*.log'  , recursive=False)]

if __name__ == "__main__":
    model = PredictiveModel()
    if len(sys.argv) == 2:
        model.scanfile(sys.argv[1])
    elif len(sys.argv) == 3:
        model.scanfile(sys.argv[1],sys.argv[2])
    else:
        print("Incorrect arguments")
    fileSummary = pd.read_csv(model.outfile + '.csv.part0')
    fileSummary["prob"], fileSummary["label"] = [model.fileProba, model.fileLabel]
    fileSummary.to_csv(model.outfile + ".csv", index=False)
    [os.remove(file_) for file_ in glob.glob(model.outfile + '*.csv.part0', recursive=False)]



