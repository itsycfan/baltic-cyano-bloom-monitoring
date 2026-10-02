# Start Here

A self-contained guide to this project, written so that it can be picked up again months later without any other context. Read this file first, then follow the links.

## 1. The project in one paragraph

Automated imaging (the Imaging FlowCytobot, IFCB) photographs plankton in sea water, and a classifier names each image. Classifiers are usually judged on single images, but monitoring uses **bloom curves**: the share of each taxon in each weekly sample over a year. This project measures how image classification errors turn into bloom-curve errors for Baltic Sea nitrogen-fixing cyanobacteria, and how much expert review is needed to fix them. Training data: SYKE IFCB images from 2016 to 2019. Test data: 47 expert-verified weekly samples from Utö in 2021. It is a retrospective evaluation in a near-real-time-capable setting.

## 2. Status (2026-10-02)

| Item | State | Where |
|---|---|---|
| Stage 0 data audit | Done | `experiments/stage0_data_audit/` |
| RQ1 representation | Concluded (`rq1-concluded`) | `experiments/stage1_rq1_representation/` |
| RQ2 abundance | Concluded (`rq2-concluded`) | `experiments/stage2_rq2_abundance/` |
| RQ3 selective review | Concluded (`rq3-concluded`) | `experiments/stage3_rq3_selective_review/` |
| Final roadmap and framework | `vFinal` | `docs/02_proposal.md`, `docs/CHANGELOG.md` |
| Project report | Done | `docs/PROJECT_REPORT.md` |
| Manuscript v1 | Draft, local only | `paper/` (git-ignored) |
| Preprint posting | Not started | see section 8 |

## 3. The results in six sentences

1. Under the shift from the training years to 2021, every feature set lost 0.19 to 0.26 macro F1; DINOv2 is the primary model, and validation from the training years did not identify the model that transferred best (the four-model fusion).
2. Bloom curves got the peak week right but were inflated outside the bloom; 70 to 85% of that over-estimation came from **unclassifiable particles** forced into known classes (an open-set problem).
3. Adjusted classify and count (ACC) removed only 1 to 17% of the error; class-balanced weights removed 44 to 66%.
4. Without review, the 2% bloom onset was signalled 3 to 4 weeks early in 9 of 14 configurations.
5. Reviewing 2 to 10% of images with the evidence-based triage policy beat ACC everywhere, but review rates set on validation data grew to 36 to 58% of images in 2021.
6. *Nodularia spumigena*, the most toxic target, had only 5 images in 47 weekly samples; a rule sending all its predictions to an expert removed every false detection at at most 0.11% of images.

## 4. Learning path

Each step lists what to read and what to look for. The glossary is in section 10.

| Step | Topic | Open |
|---|---|---|
| 1 | Why: Baltic cyanobacteria, nitrogen fixation, toxins | `docs/00_project_definition.md` (section 1.1), dataset PDFs in `data/` (page 3 shows all 50 classes) |
| 2 | How monitoring works: IFCB, samples, relative abundance, onset | `config/datasets.json`, any folder in `data/`, `experiments/stage1_rq1_representation/outputs/preprocessing_examples.png` |
| 3 | Research questions, framework, pre-registration, scope rule | `docs/02_proposal.md`, `docs/ANALYSIS_PLAN.md`, `experiments/paper_figures/fig01_framework.png` |
| 4 | Repository and reproducibility | this file (sections 5 and 6), `README.md` |
| 5 | Stage 0: main series, ground truth | `experiments/stage0_data_audit/README.md` (has a figure-reading guide), `outputs/bloom_curve_2021_ground_truth.png` |
| 6 | RQ1: frozen features, macro F1, ECE, closed vs open set | `experiments/stage1_rq1_representation/README.md`, `outputs/rq1_summary/` |
| 7 | RQ2: CC, ACC, curve metrics, error decomposition | `experiments/stage2_rq2_abundance/outputs/dinov2_vitb14/`, `experiments/summary_outputs/rq2_*.csv` |
| 8 | RQ3: kNN evidence, AUROC, review rates, high-risk rule | `experiments/stage3_rq3_selective_review/outputs/dinov2_vitb14__none/`, `experiments/summary_outputs/rq3_*.csv` |
| Then | Everything together | `docs/PROJECT_REPORT.md`, `experiments/paper_figures/FIGURES.md` |

To trace any number: report table, then `experiments/summary_outputs/`, then the stage `outputs/` CSV, then the script that wrote it, then `checkpoints/`, `features/` and `data/`.

## 5. Repository map

| Path | Content | In git |
|---|---|---|
| `config/` | Dataset paths, main-series rule, target taxa, onset thresholds | yes |
| `src/` | Shared code: `ifcb_data.py` (parsing), `features.py` (backbones, preprocessing), `classify.py` (logistic regression, metrics, temperature), `quantify.py` (CC, ACC, curve metrics), `evidence.py` (kNN), `morphology.py` (particle area), `plot_style.py` | yes |
| `experiments/stage*/` | One folder per stage: scripts, `README.md`, `outputs/` (CSV, JSON, PNG) | yes |
| `experiments/summary_outputs/` | Cross-model comparison tables | yes |
| `experiments/paper_figures/` | Numbered figures and `FIGURES.md` with draft captions | yes |
| `docs/` | Definition, literature, proposal, analysis plan, RQ mapping, logs, report, verified references | yes |
| `data/` | SYKE images and dataset PDFs (download from B2SHARE) | no |
| `features/` | Extracted features, about 1.1 GB | no (rebuild) |
| `checkpoints/` | Classifiers, predictions, kNN evidence, about 0.4 GB | no (rebuild) |
| `paper/` | Manuscript `.docx`, PDF preview, generator | no: **back it up yourself** |
| `references/` | Third-party PDFs | no |
| `.venv/` | Python environment | no (rebuild) |

The three logs: `DEV_LOG.md` records **why** (every decision and bug), `PROGRESS.md` records **when** (the overnight run of 26 September), `CHANGELOG.md` records **what changed in the plan**.

## 6. Reproduce from scratch

Tested on an Apple M2 with 8 GB of memory. Commands run from the repository root.

```bash
# 1. Environment (Python 3.11)
python3.11 -m venv .venv
.venv/bin/pip install -r requirements.txt scipy joblib

# 2. Data: download both SYKE datasets from B2SHARE and unpack them so that the paths in
#    config/datasets.json exist (data/SYKE_plankton_IFCB_2022/..., data/Plankton IFCB Uto 2021/...)

# 3. Stage 0 (about 1 minute)
.venv/bin/python experiments/stage0_data_audit/run_audit.py

# 4. Features (resumable; ResNet-18 about 18 min, DINOv2 and CLIP about 2.5 h each, BioCLIP 2 about 10 h)
for m in resnet18 dinov2_vitb14 clip_vitb16 bioclip2; do
  .venv/bin/python experiments/stage1_rq1_representation/extract_features.py --model $m
done

# 5. Validation split (the adjacency check justifies a random split; it needs ResNet-18 features)
.venv/bin/python experiments/stage1_rq1_representation/check_index_adjacency.py
.venv/bin/python experiments/stage1_rq1_representation/make_split.py

# 6. RQ1 to RQ3 for each feature set, then fusions, T1 decision and summaries
for m in resnet18 dinov2_vitb14 clip_vitb16 bioclip2; do bash experiments/run_feature_pipeline.sh $m; done
bash experiments/run_final_stage.sh

# 7. Validity checks and figures
.venv/bin/python experiments/stage2_rq2_abundance/run_threshold_filter.py
.venv/bin/python experiments/stage2_rq2_abundance/compute_particle_area.py
.venv/bin/python experiments/stage2_rq2_abundance/run_area_proxy.py
.venv/bin/python experiments/make_paper_figures.py

# 8. Optional post hoc diagnostics
.venv/bin/python experiments/stage1_rq1_representation/exploratory_size_ablation.py
.venv/bin/python experiments/stage3_rq3_selective_review/run_review.py --features dinov2_vitb14 --exclude-signal nn_distance
```

Every heavy script has a smoke-test option (`--limit`); run it first. To rebuild the manuscript (local only): `cd paper/generator && npm install docx && node build.js ../manuscript_v2.docx`.

## 7. Project rules

- **No tuning on 2021.** All choices use the 2022 validation split; 2021 is evaluated once. New analyses are pre-registered in `ANALYSIS_PLAN.md` before running; anything added after seeing results is labelled post hoc and changes no decision.
- **Scope rule** (`02_proposal.md`): a new comparison enters only if an RQ requires it or a stated conclusion depends on it; everything else is future work.
- **Numbers** in documents and the paper must come from output files; never type them from memory.
- **Git:** commit messages start with the stage or RQ; never commit `data/`, `references/` or `paper/`; never rewrite pushed history; tag concluded RQs. No AI co-author trailers in new commits (AI use is disclosed in the paper).
- **Writing:** documents, code and commits in English; the paper in British English without dashes.

## 8. Open to-dos for Yuchen

1. Confirm journal quartiles (SCImago or JCR) for the 26 journals listed at the end of `docs/REFERENCES.md`.
2. Check the SYKE dataset licence before showing example images (paper Figs. 2, S1, S10).
3. Confirm the affiliation on the manuscript.
4. Read and edit the manuscript (`paper/manuscript_v1.docx`).
5. Create a GitHub release and link it to Zenodo for a DOI; add the DOI to the paper.
6. Check arXiv and EarthArXiv policies (licence, dual posting), then post the preprint.
7. Optional: send the results to the SYKE dataset authors; consider free review through Peer Community In.
8. Decide which tentative future-work items, if any, to run (`02_proposal.md`, Future work).

## 9. Known pitfalls

- **Memory (8 GB):** kNN uses chunks of 512 queries; larger chunks swap. Run one heavy job at a time.
- **OpenAI CLIP** must be loaded with `force_quick_gelu=True` (open_clip warns otherwise). Never hide warnings in smoke tests.
- **Job queues:** do not wait on `pgrep -f <pattern>` when the waiting command contains the pattern itself (it waits forever); chain jobs sequentially or wait on a PID.
- **Unicode paths:** the test folder name contains `ö`; it works on macOS but keep it in `config/datasets.json` only.
- **Literature tools:** ScienceDirect and SCImago block automated access; use Europe PMC, Crossref, OpenAlex and doi.org, and check quartiles by hand.

## 10. Glossary

| Term | Meaning |
|---|---|
| Phytoplankton | Microscopic photosynthetic organisms drifting in water |
| Cyanobacteria | Photosynthetic bacteria; several filamentous species bloom in the Baltic in summer |
| Bloom | Rapid increase of one or a few taxa |
| Nitrogen fixation | Converting nitrogen gas into usable compounds (in heterocytes); gives some cyanobacteria an advantage when nitrogen runs out |
| HAB | Harmful algal bloom, defined by impact (for example toxins) |
| Nodularin | Liver toxin produced mainly by *Nodularia spumigena* |
| IFCB | Imaging FlowCytobot: draws about 5 mL of water and photographs particles one by one |
| Sample | One water intake and all images from it |
| Relative abundance | Images of a taxon / all images in the sample (unclassifiable included) |
| Bloom curve | Relative abundance over time |
| Onset | First week (June to September) when the curve reaches 1, 2 or 5% |
| Main series | One complete expert-verified sample per week; supplementary samples only for sensitivity |
| Unclassifiable | Images experts could not assign to any class (detritus, aggregates, unknown organisms) |
| Frozen features | Embeddings from a pretrained network used without retraining |
| Macro F1 | Mean over classes of F1; each class counts equally |
| ECE, temperature scaling | Calibration error; dividing scores by T to fix over- or under-confidence |
| Dataset shift | Training and deployment data differ (here: years) |
| Closed set, open set | Must choose a known class vs may also answer "unknown" |
| CC, ACC | Classify and count; adjusted classify and count (corrects with validation error rates) |
| kNN | The k most similar training images |
| AUROC | How well a score ranks errors above correct images; 0.5 is chance |
| Triage policy | Rules that send images to an expert |
| Nominal, realised review rate | Share flagged on validation vs in 2021 |
| Pre-registration | Writing analysis rules down before seeing test results |
