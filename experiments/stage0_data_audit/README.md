# Stage 0: Data Audit

Parses IFCB filenames into a sample table, checks weekly sampling coverage and the temporal separation between training and test data, and plots the ground-truth relative abundance of target cyanobacteria in 2021.

## Run

```bash
python3 experiments/stage0_data_audit/run_audit.py --limit 20   # smoke test, writes to outputs/smoke/
python3 experiments/stage0_data_audit/run_audit.py              # full run, about 1 minute
```

Configuration: `config/datasets.json` (paths, class counts from the dataset description, main-series rule) and `config/taxa.json` (target taxa, aggregates, onset thresholds).

## Main series

The 2021 test set mixes regular weekly samples (Tuesday around 12:00) with supplementary samples that SYKE selected to enrich rare classes. Supplementary samples are not a random draw: they over-weight some weeks and favour moments rich in rare taxa. Curve metrics therefore use a **main series** of one complete sample per ISO week, the one closest to Tuesday 12:00. Selection uses timestamps only. A sample counts as complete if images / highest particle index >= 0.5; one sample (D20210720T120102, week 29, 50 images of a single class, coverage 0.0065) fails this and is excluded. Supplementary samples are kept for sensitivity analysis only.

## Key results

- Train: 63,074 images, 50 classes, identical to the dataset description. Filenames carry no sample ID or time.
- Test: 151,235 images (57,207 classified, 94,028 unclassifiable), 48 classes (no Beads, no *Prorocentrum cordatum*), 59 samples.
- Main series: 47 samples; supplementary: 11; excluded: 1; weeks without a sample: 1, 2, 29, 41, 42.
- No byte-identical images between train and test; no corrupt images.
- Ground-truth peaks (main series): N-fixing filamentous total 9.3% (27 July), *Dolichospermum* 5.1% (29 June), Oscillatoriales 12.9% (17 August).
- Onset of the N-fixing total (June to September window): 8 June at 1%, 29 June at 2% and 5%.

> **Finding for the paper:** *Nodularia spumigena*, the most toxic target, has only 5 images in the 47 main-series samples (at most 2 per sample, peak 0.03%) and 57 in supplementary samples. It cannot be monitored as an abundance curve and is evaluated as a detection task; this supports routing it to expert review via the high-risk rule.

## Reading the ground-truth bloom curve (`bloom_curve_2021_ground_truth.png`)

Each point is one weekly sample: the share of all images in that sample (unclassifiable included) that belong to a taxon. Lines join the 47 main-series samples; hollow circles are supplementary samples, shown but not used for metrics. The dotted vertical line marks the excluded incomplete sample (20 July).

- **Upper panel, bloom-forming filamentous cyanobacteria:** N-fixing total (thick line; *Aphanizomenon* + *Dolichospermum* straight and coiled + *N. spumigena*), *Aphanizomenon flosaquae*, *Dolichospermum* total, and Oscillatoriales (dashed; filamentous, not a primary bloom taxon, reported separately).
- **Lower panel, low-abundance high-risk taxa:** *N. spumigena* and *Dinophysis acuminata*, on a y-axis about 30 times smaller.
- **Seasonal sequence:** *Dolichospermum* first (peak 5.1% on 29 June), then *Aphanizomenon* (3.7% on 6 July, maximum 8.6% on 27 July; N-fixing total 9.3%), then Oscillatoriales (12.9% on 17 August). Winter values (1 to 3% of images; 15 to 20% of particle area, see `stage2_rq2_abundance/outputs/area_proxy/`) come from a few large *Aphanizomenon* filaments in a sparse winter community: the share is high because the total is small (350 to 900 images per sample, against several thousand in summer). It is not a bloom, but relative abundance alone cannot show that.
- **Why 9.3% is a bloom:** values count images, not biomass. A long filament counts once, and more than half of each sample are small unclassifiable particles.

**External consistency with Kraft et al. (2022, section 3.2).** Their near-real-time biomass series from the same station in summer 2021 (one sample about every 20 minutes) describes the same sequence: *Dolichospermum*/*Anabaenopsis* bloomed in late June (peak 2 July) and dropped within days; *Aphanizomenon* followed (peak 5 July) and formed a third peak at the end of July; *N. spumigena* appeared only sporadically. Two independent measures (biomass at 20-minute resolution, image counts in weekly expert-verified samples) give the same seasonal pattern, which supports the ground-truth curve used in RQ2 and RQ3. They also report a secondary peak on 19 and 20 July; our week-29 sample (20 July) is incomplete and excluded, so the weekly series misses that peak. This shows the practical cost of weekly resolution: short peaks lasting a few days can fall between samples.

## Outputs (`outputs/`)

| File | Content |
|---|---|
| `image_table.csv.gz` | One row per image: dataset, class, filename, sample ID, time, ISO week, size |
| `class_counts.csv` | Images per class, train vs description vs test |
| `samples_2021.csv` | Per-sample counts, completeness, main-series flag, target relative abundances |
| `sample_class_counts_2021.csv` | Per-sample counts of every class (ground truth for Stage 2 and 3) |
| `weekly_coverage_2021.csv` | Samples per ISO week and the chosen main-series sample |
| `summary.json`, `run_config.json` | Summary numbers and the configuration of the run |
| `bloom_curve_2021_ground_truth.png` | Ground-truth bloom curves (main series lines, supplementary hollow markers) |
| `sample_coverage_2021.png` | Images per sample, classified vs unclassifiable |
| `class_counts_train_vs_test.png` | Class distribution shift between train and test |
