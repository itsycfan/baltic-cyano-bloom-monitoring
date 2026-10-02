# Baltic Cyano Bloom Monitoring

This project examines how image classification errors propagate to abundance time series of bloom-forming filamentous cyanobacteria in the Baltic Sea. It compares frozen features from vision foundation models (DINOv2, CLIP, BioCLIP 2) with an ImageNet ResNet-18 baseline, and evaluates a triage policy that routes uncertain images to human review.

Data: [SYKE-plankton_IFCB_2022](https://b2share.eudat.eu/records/abf913e5a6ad47e6baa273ae0ed6617a) (training) and [SYKE-plankton_IFCB_Utö_2021](https://b2share.eudat.eu/records/7c273b6f409c47e98a868d6517be3ae3) (testing), released by the Finnish Environment Institute (SYKE) and acquired with an Imaging FlowCytobot (IFCB). The datasets are not redistributed in this repository.

**Status (2026-10-02):** all three research questions concluded (tags `rq1-concluded` to `rq3-concluded`); final roadmap and framework at tag `vFinal`. **Start with [`docs/START_HERE.md`](docs/START_HERE.md)**: project summary, results, learning path, reproduction commands, rules and open to-dos. Full results: [`docs/PROJECT_REPORT.md`](docs/PROJECT_REPORT.md).

Main findings: under the shift from 2016 to 2019 training data to 2021, macro F1 drops by 0.19 to 0.26; bloom curves keep the right peak week but are inflated outside the bloom, mostly (70 to 85%) by unclassifiable particles that a closed-set classifier forces into known classes; adjusted classify and count removes little of this, while reviewing 2 to 10% of images selected with confidence and kNN evidence does better everywhere; review budgets set on validation data grow to 36 to 58% of images in 2021.

Built on the [template-rq-driven-research](https://github.com/itsycfan/template-rq-driven-research) template.

## Repository layout

| Folder | Content |
|---|---|
| `config/` | Dataset paths, target taxa, onset thresholds |
| `src/` | Shared code: data parsing, features, classifier, quantification, kNN evidence, plotting |
| `experiments/` | One folder per stage (Stage 0, RQ1, RQ2, RQ3) with scripts and `outputs/`; `paper_figures/` holds the numbered figures for the manuscript |
| `docs/` | Project definition, proposal, pre-registered analysis plan, logs, report, verified references |
| `data/`, `references/`, `features/`, `checkpoints/`, `paper/` | Local only (git-ignored): raw images, third-party papers, extracted features, model outputs, manuscript drafts |
