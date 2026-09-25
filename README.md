# Baltic Cyano Bloom Monitoring

This project examines how image classification errors propagate to abundance time series of bloom-forming filamentous cyanobacteria in the Baltic Sea. It compares frozen features from vision foundation models (DINOv2, CLIP, BioCLIP 2) with an ImageNet ResNet-18 baseline, and evaluates a triage policy that routes uncertain images to human review.

Data: [SYKE-plankton_IFCB_2022](https://b2share.eudat.eu/records/abf913e5a6ad47e6baa273ae0ed6617a) (training) and [SYKE-plankton_IFCB_Utö_2021](https://b2share.eudat.eu/records/7c273b6f409c47e98a868d6517be3ae3) (testing), released by the Finnish Environment Institute (SYKE) and acquired with an Imaging FlowCytobot (IFCB). The datasets are not redistributed in this repository.

Built on the [template-rq-driven-research](https://github.com/itsycfan/template-rq-driven-research) template.
