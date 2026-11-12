# Citations for the scalp EEG apps, verified on 2026-11-12

Every DOI below was fetched from Crossref or DataCite on 2026-11-12 (`scripts/verify-citations.py` does the same check on each app's CITATION.cff). Title, first author and year are **as the registry returns them**; copy every author from the registry, never from this table or from memory. Rows in the second table were found by a Crossref bibliographic query for a paper the survey cited without a DOI; re-fetch them by DOI.

## Corrections to the survey found by this check

- **Barkmeier et al. 2012** (10.1016/j.clinph.2011.09.023) is titled *High inter-reviewer variability of spike detection on intracranial EEG addressed by an automated multi-channel algorithm*: it is an **intracranial** validation. The survey's title ("... in scalp and intracranial EEG") was wrong, and the claim that the detector "was validated on scalp" must not be repeated. Likewise **Janca et al. 2014/2015** (10.1007/s10548-014-0379-1, online 2014, print 2015) is an intracranial paper. A scalp spike detector built on epycom's implementations must say so and be validated by us (see the builder brief, eeg-spikes).
- Scalp-validated classical IED detection with a verifiable record: **Lodder, Askamp & van Putten 2013** (10.1016/j.clinph.2013.05.019, smart-template database) and **Lodder & van Putten 2014** (10.1371/journal.pone.0085180, self-adapting system); neither has public code.
- **Esteller et al. 2001** (line length, 10.1109/IEMBS.2001.1020545): Crossref has no issue year; cite 2001 from the proceedings (Proc. 23rd IEEE EMBS).
- **Karatza et al.** scalp HFO consistency paper (10.1111/epi.18250): Crossref year 2024 (online), not 2025.
- **Detti et al. 2020** (10.3390/pr8070846) is titled *EEG Synchronization Analysis for Seizure Prediction: A Study on Data of Noninvasive Recordings* (Processes); it is the paper PhysioNet asks to cite for the Siena database.

## Verified DOIs

| DOI | Registry | Title (registry) | First author | Year | Venue |
|---|---|---|---|---|---|
| 10.1001/jamaneurol.2019.3485 | crossref | Development of Expert-Level Automated Detection of Epileptiform Discharges During Electroencephalogram Interpretation | Jing, Jin | 2020 | JAMA Neurology |
| 10.1001/jamaneurol.2023.1645 | crossref | Automated Interpretation of Clinical Electroencephalograms Using Artificial Intelligence | Tveit, Jesper | 2023 | JAMA Neurology |
| 10.1007/978-3-031-43993-3_18 | crossref | DeepSOZ: A Robust Deep Model for Joint Temporal and Spatial Seizure Onset Localization from Multichannel EEG Data | M. Shama, Deeksha | 2023 | Lecture Notes in Computer Science |
| 10.1007/978-3-032-04927-8_19 | crossref | EEG-DINO: Learning EEG Foundation Models via Hierarchical Self-distillation | Wang, Xujia | 2025 | Lecture Notes in Computer Science |
| 10.1007/s10548-014-0379-1 | crossref | Detection of Interictal Epileptiform Discharges Using Signal Envelope Distribution Modelling: Application to Epileptic and Non-Epileptic Intracranial Recordings | Janca, Radek | 2014 | Brain Topography |
| 10.1016/j.clinph.2011.07.050 | crossref | Automatic detection of fast oscillations (40–200 Hz) in scalp EEG recordings | von Ellenrieder, Nicolás | 2012 | Clinical Neurophysiology |
| 10.1016/j.clinph.2016.11.005 | crossref | Spike detection: Inter-reader agreement and a statistical Turing test on a large data set | Scheuer, Mark L. | 2017 | Clinical Neurophysiology |
| 10.1016/j.jneumeth.2011.06.008 | crossref | Automated EEG analysis: Characterizing the posterior dominant rhythm | Lodder, Shaun S. | 2011 | Journal of Neuroscience Methods |
| 10.1016/j.neucom.2022.11.050 | crossref | EEGraph: An open-source Python library for modeling electroencephalograms using graphs | Maitin, Ana M. | 2023 | Neurocomputing |
| 10.1016/j.neuroimage.2009.10.003 | crossref | Complex network measures of brain connectivity: Uses and interpretations | Rubinov, Mikail | 2010 | NeuroImage |
| 10.1016/j.neuroimage.2017.06.030 | crossref | Autoreject: Automated artifact rejection for MEG and EEG data | Jas, Mainak | 2017 | NeuroImage |
| 10.1016/j.neuroimage.2019.05.026 | crossref | ICLabel: An automated electroencephalographic independent component classifier, dataset, and website | Pion-Tonachini, Luca | 2019 | NeuroImage |
| 10.1016/j.nicl.2017.09.021 | crossref | Automated diagnosis of temporal lobe epilepsy in the absence of interictal spikes | Verhoeven, Thibault | 2018 | NeuroImage: Clinical |
| 10.1038/s41582-018-0055-2 | crossref | Seizure prediction — ready for a new era | Kuhlmann, Levin | 2018 | Nature Reviews Neurology |
| 10.1038/s41593-020-00744-x | crossref | Parameterizing neural power spectra into periodic and aperiodic components | Donoghue, Thomas | 2020 | Nature Neuroscience |
| 10.1038/s41597-025-04572-1 | crossref | An EEG dataset for interictal epileptiform discharge with spatial distribution information | Lin, Nan | 2025 | Scientific Data |
| 10.1038/s41597-025-05580-x | crossref | SeizeIT2: Wearable Dataset Of Patients With Focal Epilepsy | Bhagubai, Miguel | 2025 | Scientific Data |
| 10.1038/s41598-017-13064-1 | crossref | Resection of high frequency oscillations predicts seizure outcome in the individual patient | Fedele, Tommaso | 2017 | Scientific Reports |
| 10.1038/s41598-019-52700-w | crossref | High-frequency oscillations in scalp EEG mirror seizure frequency in pediatric focal epilepsy | Boran, Ece | 2019 | Scientific Reports |
| 10.1038/s41746-021-00440-5 | crossref | U-Sleep: resilient high-frequency sleep staging | Perslev, Mathias | 2021 | npj Digital Medicine |
| 10.1038/sdata.2018.308 | crossref | A mind-brain-body dataset of MRI, EEG, cognition, emotion, and peripheral physiology in young and old adults | Babayan, Anahit | 2019 | Scientific Data |
| 10.1038/sdata.2019.39 | crossref | A dataset of neonatal EEG recordings with seizure annotations | Stevenson, N. J. | 2019 | Scientific Data |
| 10.1056/AIoa2401221 | crossref | Expert-Level Detection of Epilepsy Markers in EEG on Short and Long Timescales | Li, Jun | 2025 | NEJM AI |
| 10.1088/1741-2552/ad4916 | crossref | PyHFO: lightweight deep learning-powered end-to-end high-frequency oscillations analysis application | Zhang, Yipeng | 2024 | Journal of Neural Engineering |
| 10.1093/braincomms/fcab052 | crossref | Scalp high-frequency oscillation rates are higher in younger children | Cserpan, Dorottya | 2021 | Brain Communications |
| 10.1101/2024.10.03.615261 | crossref | HBN-EEG: The FAIR implementation of the Healthy Brain Network (HBN) electroencephalography dataset | Shirazi, Seyed Yahya | 2024 |  |
| 10.1109/ICASSP.2018.8461489 | crossref | An Ensemble Learning Approach to Detect Epileptic Seizures from Long Intracranial EEG Recordings | Schiratti, J.-B. | 2018 | 2018 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP) |
| 10.1109/IEMBS.2001.1020545 | crossref | Line length: an efficient feature for seizure onset detection | Esteller, R. | None | 2001 Conference Proceedings of the 23rd Annual International Conference of the IEEE Engineering in Medicine and Biology Society |
| 10.1109/TBME.2015.2481482 | crossref | Real-time neuroimaging and cognitive monitoring using wearable dry EEG | Mullen, Tim R. | 2015 | IEEE Transactions on Biomedical Engineering |
| 10.1109/TBME.2016.2556425 | crossref | Time-Frequency Strategies for Increasing High-Frequency Oscillation Detectability in Intracerebral EEG | Roehri, Nicolas | 2016 | IEEE Transactions on Biomedical Engineering |
| 10.1109/TBME.2019.2930186 | crossref | Evaluation of Artifact Subspace Reconstruction for Automatic Artifact Components Removal in Multi-Channel EEG Recordings | Chang, Chi-Yuan | 2020 | IEEE Transactions on Biomedical Engineering |
| 10.1109/TII.2021.3133307 | crossref | EEGWaveNet: Multiscale CNN-Based Spatiotemporal Feature Extraction for EEG Seizure Detection | Thuwajit, Punnawish | 2022 | IEEE Transactions on Industrial Informatics |
| 10.1111/epi.17482 | crossref | Spike patterns surrounding sleep and seizures localize the seizure‐onset zone in focal epilepsy | Conrad, Erin C. | 2023 | Epilepsia |
| 10.1111/epi.18113 | crossref | SzCORE : Seizure Community Open‐Source Research Evaluation framework for the validation of electroencephalography ‐based automated seizure detection algorithms | Dan, Jonathan | 2024 | Epilepsia |
| 10.1111/epi.18250 | crossref | Scalp high‐frequency oscillation spatial distribution is consistent over consecutive nights, while rates vary with antiseizure medication changes | Karatza, Panagiota | 2024 | Epilepsia |
| 10.1111/j.1528-1157.1998.tb01329.x | crossref | Interictal Spiking Increases with Sleep Depth in Temporal Lobe Epilepsy | Malow, Beth A. | 1998 | Epilepsia |
| 10.1162/netn_a_00265 | crossref | FiNN: A toolbox for neurophysiological network analysis | Scherer, Maximilian | 2022 | Network Neuroscience |
| 10.13026/5d4a-j060 | datacite | Siena Scalp EEG Database | Detti, Paolo | 2020 | PhysioNet |
| 10.13026/C2K01R | datacite | CHB-MIT Scalp EEG Database | Shoeb, Ali | 2010 | physionet.org |
| 10.1371/journal.pone.0094381 | crossref | Human Intracranial High Frequency Oscillations (HFOs) Detected by Automatic Time-Frequency Analysis | Burnos, Sergey | 2014 | PLoS ONE |
| 10.1523/ENEURO.0111-23.2023 | crossref | A Two-Stage Automatic System for Detection of Interictal Epileptiform Discharges from Scalp Electroencephalograms | Wang, Xiaoyun | 2023 | eneuro |
| 10.18112/openneuro.ds003555.v1.0.1 | datacite | Dataset of EEG recordings of pediatric patients with epilepsy based on the 10-20 system | Dorottya Cserpan | 2021 | OpenNeuro |
| 10.18112/openneuro.ds005505.v1.0.1 | datacite | Healthy Brain Network (HBN) EEG - Release 1 | Seyed Yahya Shirazi | 2025 | OpenNeuro |
| 10.18112/openneuro.ds005873.v1.1.0 | datacite | SeizeIT2 | Miguel Bhagubai | 2025 | OpenNeuro |
| 10.21105/joss.01896 | crossref | MNE-BIDS: Organizing electrophysiological data into the BIDS format and facilitating their analysis | Appelhoff, Stefan | 2019 | Journal of Open Source Software |
| 10.21105/joss.04484 | crossref | MNE-ICALabel: Automatically annotating ICA components with ICLabel in Python | Li, Adam | 2022 | Journal of Open Source Software |
| 10.26275/jkbj-f3bn | datacite | Michigan High Res EEG - UMHS 0028 | William C Stacey | 2023 | Pennsieve Discover |
| 10.3389/fninf.2015.00016 | crossref | The PREP pipeline: standardized preprocessing for large-scale EEG analysis | Bigdely-Shamlo, Nima | 2015 | Frontiers in Neuroinformatics |
| 10.3389/fninf.2018.00083 | crossref | The Temple University Hospital Seizure Detection Corpus | Shah, Vinit | 2018 | Frontiers in Neuroinformatics |
| 10.3389/fninf.2023.1086634 | crossref | An accessible and versatile deep learning-based sleep stage classifier | Hanna, Jevri | 2023 | Frontiers in Neuroinformatics |
| 10.3389/fnins.2013.00267 | crossref | MEG and EEG data analysis with MNE-Python | Gramfort, Alexandre | 2013 | Frontiers in Neuroscience |
| 10.3389/fnins.2016.00196 | crossref | The Temple University Hospital EEG Data Corpus | Obeid, Iyad | 2016 | Frontiers in Neuroscience |
| 10.3390/pr8070846 | crossref | EEG Synchronization Analysis for Seizure Prediction: A Study on Data of Noninvasive Recordings | Detti, Paolo | 2020 | Processes |
| 10.48550/arXiv.2209.11007 | datacite | Avoiding Post-Processing with Event-Based Detection in Biomedical Signals | Seeuws, Nick | 2022 | arXiv |
| 10.48550/arXiv.2504.00336 | datacite | Large EEG-U-Transformer for Time-Step Level Detection Without Pre-Training | Wu, Kerui | 2025 | arXiv |
| 10.52202/079017-1239 | crossref | EEGPT: Pretrained Transformer for Universal and Reliable Representation of EEG Signals | Wang, Guagnyu | 2024 | Advances in Neural Information Processing Systems 37 |
| 10.5281/zenodo.10259996 | datacite | BIDS CHB-MIT Scalp EEG Database | Jonathan, Dan | 2023 | EPFL |
| 10.5281/zenodo.10278399 | datacite | MNE-Connectivity | Binns, Thomas S | 2026 | Zenodo |
| 10.5281/zenodo.10640762 | datacite | BIDS Siena Scalp EEG Database | Dan, Jonathan | 2024 | EPFL |
| 10.5281/zenodo.4485036 | datacite | MNE-HFO: An open-source Python implementation of HFO detection algorithms | Li, Adam | 2021 | Zenodo |
| 10.5281/zenodo.4940267 | datacite | A dataset of neonatal EEG recordings with seizures annotations | Stevenson, Nathan | 2018 | Zenodo |
| 10.5281/zenodo.5643659 | datacite | nbara/python-meegkit: v0.1.1 | Barascud, Nicolas | 2021 | Zenodo |
| 10.5281/zenodo.6363575 | datacite | PyPREP: A Python implementation of the preprocessing pipeline (PREP) for EEG data. | Appelhoff, Stefan | 2026 | Zenodo |
| 10.6084/m9.figshare.28069568.v2 | datacite | An EEG dataset for interictal epileptiform discharge with spatial distribution information | Lin, Nan | 2025 | figshare |
| 10.7554/eLife.70092 | crossref | An open-source, high-performance tool for automated sleep staging | Vallat, Raphael | 2021 | eLife |

## Found by bibliographic lookup (re-fetch by DOI before use)

| DOI | Title (registry) | Authors (first) | Year | Venue |
|---|---|---|---|---|
| 10.1016/j.clinph.2007.07.019 | The revised brain symmetry index | van Putten, Michel J.A.M. | 2007 | Clinical Neurophysiology |
| 10.1016/j.cnp.2020.11.001 | Fully automatic peak frequency estimation of the posterior dominant rhythm in a large retrospective hospital EEG cohort | Zibrandtsen, Ivan C., Kjaer, Troels W. | 2021 | Clinical Neurophysiology Practice |
| 10.1016/j.clinph.2011.09.023 | High inter-reviewer variability of spike detection on intracranial EEG addressed by an automated multi-channel algorithm | Barkmeier, Daniel T., Shah, Aashit K., Flanagan, Danny | 2012 | Clinical Neurophysiology |
| 10.1016/0013-4694(82)90038-4 | Automatic recognition of epileptic seizures in the EEG | Gotman, J. | 1982 | Electroencephalography and Clinical Neurophysiology |
| 10.1016/j.clinph.2013.05.019 | Inter-ictal spike detection using a database of smart templates | Lodder, Shaun S., Askamp, Jessica, van Putten, Michel J.A.M. | 2013 | Clinical Neurophysiology |
| 10.1371/journal.pone.0085180 | A Self-Adapting System for the Automated Detection of Inter-Ictal Epileptiform Discharges | Lodder, Shaun S., van Putten, Michel J. A. M. | 2014 | PLoS ONE |
