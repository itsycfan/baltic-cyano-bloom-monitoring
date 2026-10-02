# Verified References

Compiled 2026-10-02 for the preprint. Every entry was checked as follows; nothing was added from memory.

- **Search:** OpenAlex (title and abstract or full text), publications from 2020 onward, journal articles only, three rounds of queries per State-of-the-Art subsection.
- **DOI:** metadata confirmed in Crossref (DataCite for datasets) and registration confirmed at doi.org (HTTP 302 redirect).
- **Relevance:** abstract read for every entry (source given per entry: OpenAlex, Europe PMC, arXiv or publisher page). Full text read for Kraft et al. (2022).
- **Quartile:** SCImago could not be read automatically (bot protection), so the column gives an **expected SJR quartile that is NOT verified**. Yuchen to confirm with SCImago or JCR using the journal list at the end.

Criteria (agreed 2026-10-02): background references 2020-2026, SJR Q1/Q2 or top venue, DOI verifiable, relevance checked. Method, model and data provenance references are exempt from the year and venue criteria but must be the original source and verifiable.

## 2.1 Automated phytoplankton imaging and IFCB monitoring

| Key | Reference | DOI | Role | Abstract source | Expected SJR (unverified) | Supports |
|---|---|---|---|---|---|---|
| R01 | Kraft, K. et al. (2022). Towards operational phytoplankton recognition with automated high-throughput imaging, near-real-time data processing, and convolutional neural networks. *Frontiers in Marine Science* | [10.3389/fmars.2022.867695](https://doi.org/10.3389/fmars.2022.867695) | core | OpenAlex + full text read | Q1 | Source of both datasets; Utö near-real-time IFCB pipeline (about 2 h delay); class-specific probability thresholds for unclassifiable images; 2021 bloom sequence used for external consistency. |
| R02 | Kraft, K. et al. (2021). First Application of IFCB High-Frequency Imaging-in-Flow Cytometry to Investigate Bloom-Forming Filamentous Cyanobacteria in the Baltic Sea. *Frontiers in Marine Science* | [10.3389/fmars.2021.594144](https://doi.org/10.3389/fmars.2021.594144) | core | OpenAlex | Q1 | First IFCB study of bloom-forming filamentous cyanobacteria in the Baltic Sea; motivates image-based cyanobacteria monitoring. |
| R03 | Kraft, K. et al. (2025). Monitoring cyanobacteria blooms with complementary measurements – a similar story told using high-throughput imaging, optical sensors, light microscopy, and satellite-based methods. *Harmful Algae* | [10.1016/j.hal.2025.102865](https://doi.org/10.1016/j.hal.2025.102865) | core | OpenAlex | Q1 | In situ imaging flow cytometry gives cyanobacteria bloom patterns similar to microscopy, optical sensors and satellites; supports IFCB as a monitoring tool. |
| R04 | Agarwal, V. et al. (2023). Sub-monthly prediction of harmful algal blooms based on automated cell imaging. *Harmful Algae* | [10.1016/j.hal.2023.102386](https://doi.org/10.1016/j.hal.2023.102386) | supporting | Europe PMC | Q1 | Daily IFCB time series used to forecast HAB taxa (Pseudo-nitzschia, Dinophysis); shows downstream use of IFCB abundances. |
| R05 | Houliez, E. et al. (2023). Does prey availability influence the detection of Dinophysis spp. by the imaging FlowCytobot?. *Harmful Algae* | [10.1016/j.hal.2023.102544](https://doi.org/10.1016/j.hal.2023.102544) | supporting | Europe PMC | Q1 | IFCB increasingly used to monitor harmful algae; detection of Dinophysis can be biased; supports Dinophysis as a high-risk taxon and measurement caveats. |
| R06 | Henrichs, D. et al. (2021). Application of a convolutional neural network to improve automated early warning of harmful algal blooms. *Environmental Science and Pollution Research* | [10.1007/s11356-021-12471-2](https://doi.org/10.1007/s11356-021-12471-2) | supporting | Europe PMC | Q1-Q2 | CNN classifier for IFCB-based HAB early warning (Texas coast); classifier choice affects warning performance. |
| R07 | Fischer, A. et al. (2020). Return of the “age of dinoflagellates” in Monterey Bay: Drivers of dinoflagellate dominance examined using automated imaging flow cytometry and long‐term time series analysis. *Limnology and Oceanography* | [10.1002/lno.11443](https://doi.org/10.1002/lno.11443) | supporting | OpenAlex | Q1 | Long-term IFCB time series to study HAB-associated community shifts; abundance time series as the product of IFCB monitoring. |
| R08 | Orenstein, E. et al. (2020). The Scripps Plankton Camera system: A framework and platform for in situ microscopy. *Limnology and Oceanography: Methods* | [10.1002/lom3.10394](https://doi.org/10.1002/lom3.10394) | optional | OpenAlex | Q1 | In situ imaging system design must include human annotation and automated classification. |

## 2.2 Plankton image classification and visual foundation models

| Key | Reference | DOI | Role | Abstract source | Expected SJR (unverified) | Supports |
|---|---|---|---|---|---|---|
| R06 | Henrichs, D. et al. (2021). Application of a convolutional neural network to improve automated early warning of harmful algal blooms. *Environmental Science and Pollution Research* | [10.1007/s11356-021-12471-2](https://doi.org/10.1007/s11356-021-12471-2) | supporting | Europe PMC | Q1-Q2 | CNN classifier for IFCB-based HAB early warning (Texas coast); classifier choice affects warning performance. |
| R09 | Goodwin, M. et al. (2022). Unlocking the potential of deep learning for marine ecology: overview, applications, and outlook. *ICES Journal of Marine Science* | [10.1093/icesjms/fsab255](https://doi.org/10.1093/icesjms/fsab255) | supporting | OpenAlex | Q1 | Overview of deep learning in marine ecology; need for collaboration across ecology and data science. |
| R10 | Maracani, A. et al. (2023). In-domain versus out-of-domain transfer learning in plankton image classification. *Scientific Reports* | [10.1038/s41598-023-37627-7](https://doi.org/10.1038/s41598-023-37627-7) | core | OpenAlex | Q1 | In-domain vs out-of-domain transfer learning for plankton images; motivates comparing generic and domain-specific pretrained features. |
| R11 | Ciranni, M. et al. (2024). Computer vision and deep learning meet plankton: Milestones and future directions. *Image and Vision Computing* | [10.1016/j.imavis.2024.104934](https://doi.org/10.1016/j.imavis.2024.104934) | supporting | OpenAlex | Q1 | Review of computer vision for plankton: milestones and open problems. |
| R12 | Eerola, T. et al. (2024). Survey of automatic plankton image recognition: challenges, existing solutions and future perspectives. *Artificial Intelligence Review* | [10.1007/s10462-024-10745-y](https://doi.org/10.1007/s10462-024-10745-y) | core | OpenAlex | Q1 | Survey of plankton recognition challenges: class imbalance, dataset shift, out-of-distribution particles. |
| R13 | Bachimanchi, H. et al. (2024). Deep‐learning‐powered data analysis in plankton ecology. *Limnology and Oceanography Letters* | [10.1002/lol2.10392](https://doi.org/10.1002/lol2.10392) | supporting | OpenAlex | Q1 | Deep learning in plankton ecology, including shortcomings. |
| R14 | Kyathanahally, S. et al. (2022). Ensembles of data-efficient vision transformers as a new paradigm for automated classification in ecology. *Scientific Reports* | [10.1038/s41598-022-21910-0](https://doi.org/10.1038/s41598-022-21910-0) | core | OpenAlex | Q1 | Classifier imprecision introduces measurement noise that hinders ecological interpretation; directly motivates abundance-level evaluation. |
| R15 | Nanni, L. et al. (2025). Convolutional neural networks and vision transformers for Plankton Classification. *Ecological Informatics* | [10.1016/j.ecoinf.2025.103272](https://doi.org/10.1016/j.ecoinf.2025.103272) | supporting | OpenAlex | Q1 | CNNs vs vision transformers for plankton classification across datasets. |
| R16 | Zhong, X. et al. (2026). Self-supervised transfer learning for few-shot classification on marine plankton images. *Frontiers in Marine Science* | [10.3389/fmars.2025.1729254](https://doi.org/10.3389/fmars.2025.1729254) | supporting | OpenAlex | Q1 | Self-supervised contrastive representations for plankton classification. |
| R18 | Ong, C. et al. (2025). An evaluation of a pre-trained transformer-based self-distillation model (DINOv2) for cross-domain plant species identification. *Neural Computing and Applications* | [10.1007/s00521-025-11499-6](https://doi.org/10.1007/s00521-025-11499-6) | supporting | OpenAlex | Q1 | Evaluation of frozen DINOv2 features for cross-domain species identification. |
| R19 | Kofidis, A. et al. (2026). High-accuracy fish species identification using transfer learning on vision foundation models. *Frontiers in Marine Science* | [10.3389/fmars.2026.1754181](https://doi.org/10.3389/fmars.2026.1754181) | supporting | OpenAlex | Q1 | Transfer learning on vision foundation models for marine species identification. |

## 2.3 Dataset shift and calibration

| Key | Reference | DOI | Role | Abstract source | Expected SJR (unverified) | Supports |
|---|---|---|---|---|---|---|
| R12 | Eerola, T. et al. (2024). Survey of automatic plankton image recognition: challenges, existing solutions and future perspectives. *Artificial Intelligence Review* | [10.1007/s10462-024-10745-y](https://doi.org/10.1007/s10462-024-10745-y) | core | OpenAlex | Q1 | Survey of plankton recognition challenges: class imbalance, dataset shift, out-of-distribution particles. |
| R20 | Chen, C. et al. (2024). Producing plankton classifiers that are robust to dataset shift. *Limnology and Oceanography: Methods* | [10.1002/lom3.10659](https://doi.org/10.1002/lom3.10659) | core | OpenAlex | Q1 | Plankton classifiers that perform well in-dataset fail under dataset shift on deployment days; directly motivates the temporal-shift test. |
| R21 | Chauhan, P. et al. (2026). A Step Toward Instrument-Agnostic Plankton Classification in the Shared Label Space of IFCB and FlowCam Data. *IEEE Access* | [10.1109/access.2026.3652320](https://doi.org/10.1109/access.2026.3652320) | supporting | OpenAlex | Q1-Q2 | Domain shift between IFCB and FlowCam and class imbalance in plankton classification. |
| R22 | Dussert, G. et al. (2024). Being confident in confidence scores: calibration in deep learning models for camera trap image sequences. *Remote Sensing in Ecology and Conservation* | [10.1002/rse2.412](https://doi.org/10.1002/rse2.412) | core | OpenAlex | Q1 | Calibration of confidence scores in ecological deep learning and its consequences for downstream ecological tasks; motivates T2. |
| R30 | Bodesheim, P. et al. (2022). Pre-trained models are not enough: active and lifelong learning is important for long-term visual monitoring of mammals in biodiversity research—Individual identification and attribute prediction with image features from deep neural networks and decoupled decision models applied to elephants and great apes. *Mammalian Biology* | [10.1007/s42991-022-00224-8](https://doi.org/10.1007/s42991-022-00224-8) | optional | OpenAlex | Q2 | Pre-trained models degrade in long-term monitoring with changing conditions; need for human involvement. |

## 2.4 From classification to abundance (quantification)

| Key | Reference | DOI | Role | Abstract source | Expected SJR (unverified) | Supports |
|---|---|---|---|---|---|---|
| R14 | Kyathanahally, S. et al. (2022). Ensembles of data-efficient vision transformers as a new paradigm for automated classification in ecology. *Scientific Reports* | [10.1038/s41598-022-21910-0](https://doi.org/10.1038/s41598-022-21910-0) | core | OpenAlex | Q1 | Classifier imprecision introduces measurement noise that hinders ecological interpretation; directly motivates abundance-level evaluation. |
| R17 | Orenstein, E. et al. (2022). Machine learning techniques to characterize functional traits of plankton from image data. *Limnology and Oceanography* | [10.1002/lno.12101](https://doi.org/10.1002/lno.12101) | supporting | OpenAlex | Q1 | Functional traits such as size and biovolume from plankton images; supports the area-based biomass proxy. |
| R23 | Fiksel, J. et al. (2021). Generalized Bayes Quantification Learning under Dataset Shift. *Journal of the American Statistical Association* | [10.1080/01621459.2021.1909599](https://doi.org/10.1080/01621459.2021.1909599) | core | OpenAlex | Q1 | Quantification assumes transportable misclassification rates, which fails under dataset shift; explains why ACC helps little. |
| R24 | González, P. et al. (2024). Binary quantification and dataset shift: an experimental investigation. *Data Mining and Knowledge Discovery* | [10.1007/s10618-024-01014-1](https://doi.org/10.1007/s10618-024-01014-1) | core | OpenAlex | Q1 | Quantification methods mostly tested under prior-probability shift; behaviour under other shifts unclear. |
| R25 | Moreo, A. et al. (2025). Kernel density estimation for multiclass quantification. *Machine Learning* | [10.1007/s10994-024-06726-5](https://doi.org/10.1007/s10994-024-06726-5) | supporting | Springer page | Q1 | Current multiclass quantification (distribution matching, KDEy); context for CC and ACC as baselines. |

## 2.5 Unknown particles and open-set recognition

| Key | Reference | DOI | Role | Abstract source | Expected SJR (unverified) | Supports |
|---|---|---|---|---|---|---|
| R01 | Kraft, K. et al. (2022). Towards operational phytoplankton recognition with automated high-throughput imaging, near-real-time data processing, and convolutional neural networks. *Frontiers in Marine Science* | [10.3389/fmars.2022.867695](https://doi.org/10.3389/fmars.2022.867695) | core | OpenAlex + full text read | Q1 | Source of both datasets; Utö near-real-time IFCB pipeline (about 2 h delay); class-specific probability thresholds for unclassifiable images; 2021 bloom sequence used for external consistency. |
| R12 | Eerola, T. et al. (2024). Survey of automatic plankton image recognition: challenges, existing solutions and future perspectives. *Artificial Intelligence Review* | [10.1007/s10462-024-10745-y](https://doi.org/10.1007/s10462-024-10745-y) | core | OpenAlex | Q1 | Survey of plankton recognition challenges: class imbalance, dataset shift, out-of-distribution particles. |
| R26 | Pastore, V. et al. (2020). Annotation-free learning of plankton for classification and anomaly detection. *Scientific Reports* | [10.1038/s41598-020-68662-3](https://doi.org/10.1038/s41598-020-68662-3) | supporting | OpenAlex | Q1 | Plankton classification with anomaly detection for unknown particles. |

## 2.6 Human-in-the-loop and selective review

| Key | Reference | DOI | Role | Abstract source | Expected SJR (unverified) | Supports |
|---|---|---|---|---|---|---|
| R08 | Orenstein, E. et al. (2020). The Scripps Plankton Camera system: A framework and platform for in situ microscopy. *Limnology and Oceanography: Methods* | [10.1002/lom3.10394](https://doi.org/10.1002/lom3.10394) | optional | OpenAlex | Q1 | In situ imaging system design must include human annotation and automated classification. |
| R27 | Schröder, S. et al. (2020). MorphoCluster: Efficient Annotation of Plankton Images by Clustering. *Sensors* | [10.3390/s20113060](https://doi.org/10.3390/s20113060) | supporting | OpenAlex | Q1-Q2 | Interactive annotation of large plankton image sets; expert time as the bottleneck. |
| R28 | Miao, Z. et al. (2021). Iterative human and automated identification of wildlife images. *Nature Machine Intelligence* | [10.1038/s42256-021-00393-0](https://doi.org/10.1038/s42256-021-00393-0) | core | arXiv abstract | Q1 | Human-in-the-loop identification reaches about 90% accuracy with about 20% of human annotations; closest analogue to selective expert review. |
| R29 | Kellenberger, B. et al. (2020). AIDE: Accelerating image‐based ecological surveys with interactive machine learning. *Methods in Ecology and Evolution* | [10.1111/2041-210x.13489](https://doi.org/10.1111/2041-210x.13489) | supporting | OpenAlex | Q1 | Human and model feedback loop for ecological image surveys. |
| R30 | Bodesheim, P. et al. (2022). Pre-trained models are not enough: active and lifelong learning is important for long-term visual monitoring of mammals in biodiversity research—Individual identification and attribute prediction with image features from deep neural networks and decoupled decision models applied to elephants and great apes. *Mammalian Biology* | [10.1007/s42991-022-00224-8](https://doi.org/10.1007/s42991-022-00224-8) | optional | OpenAlex | Q2 | Pre-trained models degrade in long-term monitoring with changing conditions; need for human involvement. |

## 2.7 Baltic Sea cyanobacteria blooms and early warning

| Key | Reference | DOI | Role | Abstract source | Expected SJR (unverified) | Supports |
|---|---|---|---|---|---|---|
| R02 | Kraft, K. et al. (2021). First Application of IFCB High-Frequency Imaging-in-Flow Cytometry to Investigate Bloom-Forming Filamentous Cyanobacteria in the Baltic Sea. *Frontiers in Marine Science* | [10.3389/fmars.2021.594144](https://doi.org/10.3389/fmars.2021.594144) | core | OpenAlex | Q1 | First IFCB study of bloom-forming filamentous cyanobacteria in the Baltic Sea; motivates image-based cyanobacteria monitoring. |
| R03 | Kraft, K. et al. (2025). Monitoring cyanobacteria blooms with complementary measurements – a similar story told using high-throughput imaging, optical sensors, light microscopy, and satellite-based methods. *Harmful Algae* | [10.1016/j.hal.2025.102865](https://doi.org/10.1016/j.hal.2025.102865) | core | OpenAlex | Q1 | In situ imaging flow cytometry gives cyanobacteria bloom patterns similar to microscopy, optical sensors and satellites; supports IFCB as a monitoring tool. |
| R05 | Houliez, E. et al. (2023). Does prey availability influence the detection of Dinophysis spp. by the imaging FlowCytobot?. *Harmful Algae* | [10.1016/j.hal.2023.102544](https://doi.org/10.1016/j.hal.2023.102544) | supporting | Europe PMC | Q1 | IFCB increasingly used to monitor harmful algae; detection of Dinophysis can be biased; supports Dinophysis as a high-risk taxon and measurement caveats. |
| R31 | Karlson, B. et al. (2021). Harmful algal blooms and their effects in coastal seas of Northern Europe. *Harmful Algae* | [10.1016/j.hal.2021.101989](https://doi.org/10.1016/j.hal.2021.101989) | core | OpenAlex | Q1 | Review of harmful algal blooms in northern European seas including the Baltic Sea. |
| R32 | Kahru, M. et al. (2020). Cyanobacterial blooms in the Baltic Sea: Correlations with environmental factors. *Harmful Algae* | [10.1016/j.hal.2019.101739](https://doi.org/10.1016/j.hal.2019.101739) | supporting | Europe PMC | Q1 | Baltic cyanobacteria blooms occur almost every summer; prediction capability is poorly developed. |
| R33 | Munkes, B. et al. (2021). Cyanobacteria blooms in the Baltic Sea: a review of models and facts. *Biogeosciences* | [10.5194/bg-18-2347-2021](https://doi.org/10.5194/bg-18-2347-2021) | core | OpenAlex | Q1 | Review of Baltic cyanobacteria bloom dynamics: nitrogen fixation, eutrophication, controls. |
| R34 | Almuhtaram, H. et al. (2021). State of knowledge on early warning tools for cyanobacteria detection. *Ecological Indicators* | [10.1016/j.ecolind.2021.108442](https://doi.org/10.1016/j.ecolind.2021.108442) | core | OpenAlex | Q1 | Early warning tools for cyanobacteria must detect bloom onset and toxin producers; motivates onset metrics. |
| R35 | Löptien, U. & Dietze, H. (2022). Retracing cyanobacteria blooms in the Baltic Sea. *Scientific Reports* | [10.1038/s41598-022-14880-w](https://doi.org/10.1038/s41598-022-14880-w) | supporting | OpenAlex | Q1 | Late-summer blooms, toxins and nitrogen input in the Baltic Sea. |
| R36 | Karlson, B. et al. (2022). A suggested climate service for cyanobacteria blooms in the Baltic Sea – Comparing three monitoring methods. *Harmful Algae* | [10.1016/j.hal.2022.102291](https://doi.org/10.1016/j.hal.2022.102291) | core | OpenAlex | Q1 | Comparison of microscopy, satellite and phycocyanin monitoring of Baltic cyanobacteria; need for multi-method observation. |
| R37 | Recknagel, F. et al. (2025). Early warning of harmful cyanobacteria blooms based on high frequency in situ monitoring and intelligible machine learning modelling: The case study of Lake Müggelsee (Germany). *Water Research* | [10.1016/j.watres.2025.124514](https://doi.org/10.1016/j.watres.2025.124514) | supporting | OpenAlex | Q1 | Early warning of cyanobacteria blooms from high-frequency in situ data and interpretable ML. |
| R38 | Chen, G. et al. (2021). Comprehensive insights into the occurrence and toxicological issues of nodularins. *Marine Pollution Bulletin* | [10.1016/j.marpolbul.2020.111884](https://doi.org/10.1016/j.marpolbul.2020.111884) | core | Europe PMC | Q1 | Nodularins, mainly produced by Nodularia spumigena, and their adverse effects; supports N. spumigena as high-risk taxon. |
| R39 | Olofsson, M. et al. (2020). Nitrogen fixation estimates for the Baltic Sea indicate high rates for the previously overlooked Bothnian Sea. *Ambio* | [10.1007/s13280-020-01331-x](https://doi.org/10.1007/s13280-020-01331-x) | supporting | OpenAlex | Q1 | Nitrogen fixation by summer filamentous cyanobacteria blooms in the Baltic Sea. |

## Method, model and data provenance (exception)

| Key | Reference | Identifier | Used for | Verified via |
|---|---|---|---|---|
| M01 | Olson, R. J., & Sosik, H. M. (2007). A submersible imaging-in-flow instrument to analyze nano- and microplankton: Imaging FlowCytobot. *Limnology and Oceanography: Methods* | [10.4319/lom.2007.5.195](https://doi.org/10.4319/lom.2007.5.195) | IFCB instrument (data acquisition) | Crossref + doi.org |
| M02 | Laakso, L., et al. (2018). 100 years of atmospheric and marine observations at the Finnish Utö Island in the Baltic Sea. *Ocean Science* | [10.5194/os-14-617-2018](https://doi.org/10.5194/os-14-617-2018) | Utö station description | Crossref + doi.org |
| M03 | Forman, G. (2008). Quantifying counts and costs via classification. *Data Mining and Knowledge Discovery* | [10.1007/s10618-008-0097-y](https://doi.org/10.1007/s10618-008-0097-y) | Adjusted classify and count (method used) | Crossref + doi.org |
| M04 | He, K., Zhang, X., Ren, S., & Sun, J. (2016). Deep residual learning for image recognition. *CVPR 2016* | [10.1109/CVPR.2016.90](https://doi.org/10.1109/CVPR.2016.90) | ResNet-18 backbone | Crossref + doi.org |
| M05 | Oquab, M., et al. (2024). DINOv2: Learning robust visual features without supervision. *Transactions on Machine Learning Research* | arXiv:2304.07193 | DINOv2 backbone | arXiv + HAL record (journal title TMLR, 2024) |
| M06 | Radford, A., et al. (2021). Learning transferable visual models from natural language supervision. *ICML 2021, PMLR 139, 8748-8763* | arXiv:2103.00020 | CLIP backbone | PMLR page |
| M07 | Gu, J., et al. (2025). BioCLIP 2: Emergent properties from scaling hierarchical contrastive learning. *NeurIPS 2025 (spotlight)* | arXiv:2505.23883 | BioCLIP 2 backbone | arXiv + OpenReview venue field |
| M08 | Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On calibration of modern neural networks. *ICML 2017, PMLR 70, 1321-1330* | arXiv:1706.04599 | Temperature scaling (method used) | PMLR page |
| M09 | Kraft, K., et al. (2022). SYKE-plankton_IFCB_2022 (dataset). *B2SHARE* | [10.23728/b2share.abf913e5a6ad47e6baa273ae0ed6617a](https://doi.org/10.23728/b2share.abf913e5a6ad47e6baa273ae0ed6617a) | Training data | DataCite DOI via doi.org |
| M10 | Kraft, K., Haraguchi, L., Velhonoja, O., & Seppälä, J. (2022). SYKE-plankton_IFCB_Utö_2021 (dataset). *B2SHARE* | [10.23728/b2share.7c273b6f409c47e98a868d6517be3ae3](https://doi.org/10.23728/b2share.7c273b6f409c47e98a868d6517be3ae3) | Test data | DataCite DOI via doi.org |

To add when used: scikit-learn (Pedregosa et al., 2011, JMLR) and PyTorch, if software is cited; verify before adding.

## Excluded candidates

- *Environmental window of cyanobacteria bloom occurrence* (J. Mar. Syst., 2021, 10.1016/j.jmarsys.2021.103618): abstract could not be read (publisher page blocks automated access); not essential.
- Two University of Helsinki repository records (10.60910/w8gn-ptwh, 10.60910/y3h3-jj8t) on Baltic cyanobacteria recruitment and *Aphanizomenon* heterocysts: repository versions, no journal version found.
- Open-set plankton recognition: no 2020-2026 journal article found; the topic is covered through R12 (survey), R26 (anomaly detection) and Kraft et al. (2022) thresholds. arXiv preprints were not used.
- Off-topic search hits (for example COVID-19 prevalence, building moisture) were discarded.

## Journals to check in SCImago or JCR

| Journal | ISSN-L | SCImago search |
|---|---|---|
| Frontiers in Marine Science | 2296-7745 | https://www.scimagojr.com/journalsearch.php?q=2296-7745 |
| Harmful Algae | 1568-9883 | https://www.scimagojr.com/journalsearch.php?q=1568-9883 |
| Environmental Science and Pollution Research | 0944-1344 | https://www.scimagojr.com/journalsearch.php?q=0944-1344 |
| Limnology and Oceanography | 0024-3590 | https://www.scimagojr.com/journalsearch.php?q=0024-3590 |
| Limnology and Oceanography: Methods | 1541-5856 | https://www.scimagojr.com/journalsearch.php?q=1541-5856 |
| ICES Journal of Marine Science | 1054-3139 | https://www.scimagojr.com/journalsearch.php?q=1054-3139 |
| Scientific Reports | 2045-2322 | https://www.scimagojr.com/journalsearch.php?q=2045-2322 |
| Image and Vision Computing | 0262-8856 | https://www.scimagojr.com/journalsearch.php?q=0262-8856 |
| Artificial Intelligence Review | 0269-2821 | https://www.scimagojr.com/journalsearch.php?q=0269-2821 |
| Limnology and Oceanography Letters | 2378-2242 | https://www.scimagojr.com/journalsearch.php?q=2378-2242 |
| Ecological Informatics | 1574-9541 | https://www.scimagojr.com/journalsearch.php?q=1574-9541 |
| Neural Computing and Applications | 0941-0643 | https://www.scimagojr.com/journalsearch.php?q=0941-0643 |
| IEEE Access | 2169-3536 | https://www.scimagojr.com/journalsearch.php?q=2169-3536 |
| Remote Sensing in Ecology and Conservation | 2056-3485 | https://www.scimagojr.com/journalsearch.php?q=2056-3485 |
| Journal of the American Statistical Association | 0162-1459 | https://www.scimagojr.com/journalsearch.php?q=0162-1459 |
| Data Mining and Knowledge Discovery | 1384-5810 | https://www.scimagojr.com/journalsearch.php?q=1384-5810 |
| Machine Learning | 0885-6125 | https://www.scimagojr.com/journalsearch.php?q=0885-6125 |
| Sensors | 1424-8220 | https://www.scimagojr.com/journalsearch.php?q=1424-8220 |
| Nature Machine Intelligence | 2522-5839 | https://www.scimagojr.com/journalsearch.php?q=2522-5839 |
| Methods in Ecology and Evolution | 2041-210X | https://www.scimagojr.com/journalsearch.php?q=2041-210X |
| Mammalian Biology | 1616-5047 | https://www.scimagojr.com/journalsearch.php?q=1616-5047 |
| Biogeosciences | 1726-4170 | https://www.scimagojr.com/journalsearch.php?q=1726-4170 |
| Ecological Indicators | 1470-160X | https://www.scimagojr.com/journalsearch.php?q=1470-160X |
| Water Research | 0043-1354 | https://www.scimagojr.com/journalsearch.php?q=0043-1354 |
| Marine Pollution Bulletin | 0025-326X | https://www.scimagojr.com/journalsearch.php?q=0025-326X |
| Ambio | 0044-7447 | https://www.scimagojr.com/journalsearch.php?q=0044-7447 |
