import sys
import os
import re
import subprocess
import pandas as pd

import petljakapi
import petljakapi.inserts
import petljakapi.select
import petljakapi.update
from petljakapi import q
filepath = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(filepath, "SraRunTable.txt")) as f:
    importing = pd.read_csv(f, sep = ",")

with open(os.path.join(filepath, "gambaro_meta.txt")) as f:
    meta = pd.read_csv(f, sep = "\t")

meta = meta[meta["Study"] == "Q-CROC-01"]

print(importing)
db = "petljakdb"

study_id = petljakapi.select.simple_select(db=db, table="studies", filter_column="ncbi_bioproject_id", filter_value="PRJNA635121")
if study_id:
    study_id = study_id[0][0]
else:
    study_id = petljakapi.inserts.generic_insert({'rname':'gambaro2021', 'study_pmid':'33931971', 'ncbi_bioproject_id':'PRJNA635121'}, "studies", db)[0][0]


## First import normals
for index,row in meta[meta["Tissue type"] == "Blood Normal"].iterrows():
    ## Check if we already inserted this sample, skip if so
    pat = row["Patient"]
    pat_nm = f"gambaro_{pat}"
    pat_record = petljakapi.select.multi_select(db, "patients", {'rname':pat_nm})
    if pat_record:
        if petljakapi.select.multi_select(db, "samples", {"patient_id":pat_record[0][0]}):
            continue
    ## Check that there's actually a paired post-tx sample
    pat_samps = meta[meta["Patient"] == pat]
    if pat_samps[pat_samps["Pre or Post-treatment for LM"] != "NaN"].shape[0] == 0:
        continue
    if pat_samps[pat_samps["Pre or Post-treatment for LM"] == "Pre"].shape[0] == 0 or pat_samps[pat_samps["Pre or Post-treatment for LM"] == "Post"].shape[0] == 0:
        continue
    
    ## Now check that it was actually sequenced, and add it to the db
    ### BioSample
    sn = row["Sample name"]
    ret = importing[importing["isolate"].str.contains(sn)]
    if ret.shape[0] == 0:
        continue
    bs = ret["BioSample"].iloc[0]
    #print(bs)

    pid = petljakapi.inserts.generic_insert({'rname':pat_nm, "study_id":study_id}, "patients", db)
    sid = petljakapi.inserts.generic_insert({'rname':sn, "study_id":study_id, "biosample_id":bs, "treatment":"blood", "patient_id":pid[0][0]}, "samples", db)[0][0]

    petljakapi.update.update(db, "patients", {'rname':pat_nm}, "germline_sample", sid)


    #rint(sn)
    #rint(importing[importing["isolate"] == sn])
    #sid = petljakapi.inserts.generic_insert({'rname':samp, "study_id":study_id, "biosample_id":bs, "treatment":"blood", "patient_id":pat_id}, "samples", db)[0][0]
    #petljakapi.update.update(db, "patients", {'rname':pat_name}, "germline_sample", sid)
    

    
    #pat_name = re.sub("(KTN[0-9]*)[A-Z|a-z]*", "\\1", row["Sample Name"])
    #pat_id = petljakapi.inserts.generic_insert({'rname':pat_name}, "patients", db)[0]
    #pat_name = pat_id[1]
    #pat_id = pat_id[0]
    #samp = row["Sample Name"]
    #bs = row["BioSample"]
    #sid = petljakapi.inserts.generic_insert({'rname':samp, "study_id":study_id, "biosample_id":bs, "treatment":"blood", "patient_id":pat_id}, "samples", db)[0][0]
    #petljakapi.update.update(db, "patients", {'rname':pat_name}, "germline_sample", sid)



for index,row in meta.iterrows():
    ## Get patient info, skip if not added (meaning no normal)
    pat = row["Patient"]
    pat_nm = f"gambaro_{pat}"
    pat_record = petljakapi.select.multi_select(db, "patients", {'rname':pat_nm})
    if not pat_record:
        continue


    if str(row["Chemotherapy Treatment"]) in ["NaN", "nan", None]:
        continue
    print(str(row["Chemotherapy Treatment"]))
    ## Get BioSample
    sn = row["Sample name"]
    ret = importing[importing["isolate"].str.contains(sn)]
    if ret.shape[0] == 0:
        continue
    bs = ret["BioSample"].iloc[0]
    sra_id = ret["Run"].iloc[0]

    ## Skip bloods
    if row["Tissue type"] == "Blood Normal":
        sid = petljakapi.select.multi_select(db, "samples", {"rname":sn})[0][0]
        petljakapi.inserts.generic_insert({'rname':sra_id, "sample_id":sid, "study_id":study_id, "source":"SRA", "sra_id":sra_id, "sequencing_strategy":"WXS"}, "runs", db)
        continue


    if str(row["Pre or Post-treatment for LM"]) in ["NaN", "nan", None]:
        continue
    elif row["Pre or Post-treatment for LM"] == "Pre":
        tx = None
    elif row["Chemotherapy Treatment"] == "Irinotecan":
        tx = "FOLFIRI"
    elif row["Chemotherapy Treatment"] == "Oxaliplatin":
        tx = "FOLFOX"
    elif row["Chemotherapy Treatment"] == "Oxaliplatin + Irinotecan":
        tx = "FOLFIRINOX"
    else:
        raise ValueError(row["Chemotherapy Treatment"])
    
    if row["Bevacizumab"] == "Yes" and tx is not None:
        tx = tx + "-Bev"

    pat_id = petljakapi.select.multi_select(db, "patients", {'rname':pat_nm})


    
    if pat_id:
        sid = petljakapi.inserts.generic_insert({'rname':sn, 'study_id':study_id, "biosample_id":bs, "treatment":tx, "patient_id":pat_id[0][0]}, "samples", db)[0][0]
        petljakapi.inserts.generic_insert({'rname':sra_id, "sample_id":sid, "study_id":study_id, "source":"SRA", "sra_id":sra_id, "sequencing_strategy":"WXS"}, "runs", db)



    ## Here's the logic: CROC-01 
    ## For the Tx column, we do this:
    ## Pre, 01-{chemo}, 02-{chemo}
    #treatment = row["treatment"]
    #pat_name = re.sub("(KTN[0-9][0-9][0-9]).*", "\\1", row["Sample Name"])
    #print(pat_name)
    #pat_id = petljakapi.select.multi_select(db, "patients", {'rname':pat_name})
    #if pat_id:
    #    print(pat_id)
        #sid = petljakapi.inserts.generic_insert({'rname':sample_name, 'study_id':study_id, "biosample_id":biosample_id, "treatment":treatment, "patient_id":pat_id[0][0]}, "samples", db)[0][0]
        #petljakapi.inserts.generic_insert({'rname':sra_id, "sample_id":sid, "study_id":study_id, "source":"SRA", "sra_id":sra_id, "sequencing_strategy":"WXS"}, "runs", db)
