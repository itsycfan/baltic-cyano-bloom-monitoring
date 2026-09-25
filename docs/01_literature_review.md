# Literature Review & Gap Analysis (SOP-1, step 5)

## Sources reviewed

| Source | Year | Approach | Result / claim | Relevant to |
|---|---|---|---|---|
| Olson & Sosik, Limnol. Oceanogr. Methods 5:195 (doi:10.4319/lom.2007.5.195) | 2007 | Imaging FlowCytobot instrument | Automated imaging-in-flow of nano- and microplankton | Data acquisition |
| Kraft et al., Front. Mar. Sci. 8:282 (doi:10.3389/fmars.2021.594144) | 2021 | High-frequency IFCB imaging at Utö | First IFCB study of bloom-forming filamentous cyanobacteria in the Baltic Sea | Target taxa, domain context |
| Kraft et al., Front. Mar. Sci. 9 (doi:10.3389/fmars.2022.867695) | 2022 | CNN with near-real-time processing at Utö | Operational phytoplankton recognition; source of both datasets | Baseline, data |
| Laakso et al., Ocean Sci. 14:617 (doi:10.5194/os-14-617-2018) | 2018 | Long-term station records | Description of the Utö observation site | Site context |
| BioCLIP 2, NeurIPS 2025 (arXiv:2505.23883) | 2025 | Hierarchical contrastive training on TreeOfLife-200M | Biological foundation model with emergent properties beyond species labels | RQ1 candidate |
| Open-Set Plankton Recognition (arXiv:2503.11318) | 2025 | Open-set recognition on SYKE ZooScan and IFCB data | Rejection of unknown classes in plankton images | Evidence layer |
| Planktonzilla (arXiv:2606.00080) | 2026 | Large multimodal plankton dataset, CLIP-based and supervised models | BioCLIP and BioCLIP 2 transfer poorly; supervised classifiers perform best | RQ1 gap |

To verify before citation: Sosik & Olson (2007) on automated IFCB classification; Forman (2008) on quantification and adjusted classify-and-count; González et al. (2017, 2019) on plankton quantification; Moreo et al. on the QuaPy library; Oquab et al. (2024) on DINOv2; Radford et al. (2021) on CLIP; Kahru & Elmgren (2014) on satellite time series of Baltic cyanobacteria blooms.

## What exists

IFCB imaging with CNN classification is operational at Utö and has been used to follow filamentous cyanobacteria at high temporal resolution (Kraft et al., 2021, 2022). Model evaluation in plankton recognition centres on per-image accuracy, and quantification methods that correct class counts exist in the machine learning and plankton literature.

Vision foundation models are now tested on plankton images. Recent evidence indicates that general biological foundation models transfer poorly in direct classification and that supervised models remain stronger (Planktonzilla, 2026). Open-set methods address particles outside the known classes.

## Where it falls short

- **Gap 1 (RQ1):** foundation-model features have been compared mainly at the image level, not under a real temporal shift to complete natural samples.
- **Gap 2 (RQ2):** the effect of classifier choice on bloom curve properties (onset, peak timing, peak magnitude) for Baltic cyanobacteria has not been quantified.
- **Gap 3 (RQ3):** the trade-off between expert review workload and abundance error has not been measured, although expert verification is part of operational practice.

## Open questions carried forward

- Target class set and bloom onset definition (from `00_project_definition.md` §4.5).
- Whether the zero-shot performance of BioCLIP 2 on IFCB images is as limited as expected, given the domain gap and the non-taxonomic class distinctions (coiled forms, chain or single cells, calibration beads, detached heterocytes). Treated as an optional ablation.

---

Once the gaps are clear, continue to [`02_proposal.md`](02_proposal.md).
