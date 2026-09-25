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
