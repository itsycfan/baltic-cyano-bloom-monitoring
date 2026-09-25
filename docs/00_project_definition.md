# Project Definition (SOP-1, steps 1 to 4)

## 1. Background & Motivation

Filamentous cyanobacteria form recurrent summer blooms in the Baltic Sea, and some taxa produce toxins. Imaging flow cytometry with the Imaging FlowCytobot (IFCB), combined with automated image classification, already supports near-real-time phytoplankton monitoring in the region (Kraft et al., 2022). Classifiers in this field are usually evaluated by per-image accuracy on curated test sets, whereas bloom monitoring and early warning rely on sample-level abundance time series. The relation between the two has not been systematically assessed.

The project also transfers methods developed for visual inspection in manufacturing (feature fusion, confidence-aware decision rules, human-AI collaboration) to ocean monitoring.

### 1.1 Key terms

- **Phytoplankton:** drifting photosynthetic microorganisms, including diatoms, dinoflagellates, cryptophytes, green algae and cyanobacteria.
- **Bloom-forming filamentous cyanobacteria:** in the Baltic Sea mainly *Aphanizomenon*, *Dolichospermum* and *Nodularia*. Their heterocytes fix atmospheric nitrogen, which favours them in nitrogen-limited, phosphorus-rich summer conditions.
- **Harmful algal bloom (HAB):** defined by impact rather than taxonomy. Some cyanobacteria blooms are harmful (*Nodularia spumigena* produces nodularin), some HABs are not cyanobacteria (*Dinophysis acuminata* produces diarrhetic shellfish toxins even at low density), and not every bloom is harmful.
- **Relative abundance:** the number of images of a taxon divided by all images in a sample.
- **Bloom curve:** relative abundance over time. Onset, peak timing, peak magnitude and duration are the quantities used for monitoring and warning.

### 1.2 Data

Both datasets were released by the Finnish Environment Institute (SYKE). Images were acquired with an IFCB and annotated by expert taxonomists into 50 classes.

- **SYKE-plankton_IFCB_2022 (training):** about 63,000 images. Sources are continuous deployment at the Utö station in 2017 and 2018 (62 samples) and Alg@line ferrybox samples from 2016 and 2019 run in the laboratory (52 samples). Some file names retain earlier class names.
- **SYKE-plankton_IFCB_Utö_2021 (testing):** continuous deployment at Utö from January to December 2021, with about one sample per week plus additional seasonal samples for rare classes. All images in each selected sample were verified or corrected, and images that could not be identified are stored in a separate unclassifiable folder. Sample composition is therefore complete. Reported sizes differ (about 140,000 images in the dataset description; about 57,000 classified and 94,000 unclassifiable in the repository record) and will be confirmed by counting.
- **Main series:** the regular weekly samples form the main time series (one complete sample per ISO week, closest to Tuesday 12:00); supplementary samples chosen for rare classes are kept for sensitivity analysis only. See `02_proposal.md`, Stage 0.
- **File names:** for example `D20210601T120001_IFCB114_01623.png`, giving the sample start time, the instrument (IFCB114) and the particle index. The first two fields form the sample ID.

Training (2016 to 2019) and test (2021) data do not overlap in time, so the seasonal distribution shift is real rather than simulated.

## 2. Stakeholders

| Name | Role | Vault entity link |
|---|---|---|
| Yuchen Fan | Lead researcher | |
| Supervisors, Politecnico di Torino | Academic supervision | |
| SYKE Marine Research Centre (K. Kraft, J. Seppälä) | Data owners and dataset contacts | |

## 3. Target Output

- Type: conference paper.
- Venue / deadline: Computer Vision Conference (CVC) 2027, Amsterdam, 15 to 16 April 2027. Springer LNNS, double-blind review, main text up to 18 pages, virtual presentation available. Submission deadline as listed at https://saiconference.com/CVC.

## 4. Problem Framing

### 4.1 Observations

- Plankton image recognition studies mostly report per-image accuracy on curated test sets.
- Class proportions change strongly across seasons, so a small error rate on an abundant class can exceed the true count of a rare class.
- Natural samples contain many particles outside the known classes, which a closed-set classifier assigns to known classes.
- The most toxic target taxon, *Nodularia spumigena*, has 169 training images, while the largest cyanobacteria class has 12,280.
- Expert verification is already part of operational practice: the 2021 test labels were produced by taxonomists who checked model predictions.
- General biological foundation models transfer poorly to plankton images in direct classification (Planktonzilla, 2026).

### 4.2 Problem Statement

It is not known how per-image classification errors translate into errors in sample-level abundance time series of bloom-forming cyanobacteria, or how much expert review is needed to keep these errors acceptable.

### 4.3 Scope Exclusion

- **Accuracy benchmarking alone:** already addressed by recent work and not sufficient for monitoring.
- **Vision-language model reasoning:** the VLM layer of the original framework is excluded because of its cost at this image volume and its uncertain reliability on grayscale microscopy. It is left for future work.
- **End-to-end fine-tuning of large backbones:** outside the time budget. Frozen features are used.
- **Biomass or concentration:** sample volumes are not included in the datasets, so only relative abundance is estimated.
- **Bloom forecasting:** the project evaluates the observation layer that forecasting relies on, not forecasting itself.

### 4.4 Preliminary Goal

Quantify the error of cyanobacteria relative abundance curves produced by frozen-feature classifiers on the 2021 Utö samples, and the error reduction achieved by algorithmic correction and by selective human review at different review rates.

### 4.5 Open Questions

- Final set of target classes, to be confirmed against Kraft et al. (2021, 2022).
- ~~Definition of bloom onset~~ Resolved in Stage 0: fixed thresholds of 1%, 2% and 5% within June to September (see `02_proposal.md`).
- ~~Whether the additional seasonal samples allow a clean series of one sample per week~~ Resolved in Stage 0: 47 main-series samples, 5 weeks without a sample.
- Whether feature fusion improves transfer, and whether classifier confidence remains calibrated under the temporal shift.

---

Once this is stable, continue to [`01_literature_review.md`](01_literature_review.md).
