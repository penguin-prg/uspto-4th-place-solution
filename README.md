
This is the 4th Place Solution for the USPTO - Explainable AI for Patent Professionals (Kaggle competition).

- detail document: https://www.kaggle.com/competitions/uspto-explainable-ai/discussion/522200
- submission code (with magic): https://www.kaggle.com/code/ryotayoshinobu/uspto-4th-place-solution-w-magic-lb0-98
- submission code (without magic): https://www.kaggle.com/code/ryotayoshinobu/uspto-4th-place-solution-w-o-magic-lb0-91


# How to Reproduce (for Competition Organizers)
## Hardware
- CPU: Intel Core i9 13900KF (24 cores, 32 threads)
- GPU: NVIDIA GeForce RTX 4090
- RAM: 64GB

## OS/platform
- WSL2 (version 2.0.9.0, Ubuntu 22.04.2 LTS)

## 3rd-party software
Please check the dockerfile in `/kaggle/.devcontainer`

## Preprocess
### Solution with magic
1. put the competition data in `input/uspto-boolean-search-optimization`
    - ex. input/uspto-boolean-search-optimization/test.csv
2. put the whoosh wheel in `input/whoosh-wheel-2-7-4`
    - (`input/whoosh-wheel-2-7-4/Whoosh-2.7.4-py2.py3-none-any.whl`)
2. save tokenized text data
    - `input/all-index/gen.ipynb`
    - `input/all-index-per-patent/split.ipynb`
        - Too many files may cause errors along the way. In that case, run it again (the rest will be saved in a separate directory).
    - `input/all-index-per-patent/split/gen_db.ipynb`
3. count cpc frequency
    - `input/cpc-counts/cpc_freq.ipynb`
4. count token frequency
    - `input/token-counts/word_freq.ipynb`
5. generate DB for mapping rare_token to patents
    - `input/rare-tokens/gen.ipynb`
    - `input/rare-tokens/save_db.ipynb`
6. generate DB for mapping patent to cpcs
    - `input/patent2cpc/save_db.ipynb`

### Only Solution without magic
1. complete all steps above (1.~6.)
3. generate .json for mapping cpc to patents
    - `input/cpc-mapping/cpc_mapping.ipynb`
2. generate DB for (cpc, token) to patents
    - `input/preprocess-complete/save_cpc_token_lists.ipynb`
    - `input/preprocess-complete/save_patent_wise.ipynb`
    - `input/preprocess-complete/split/gen_leveldb.ipynb`
    - `input/preprocess-complete-v2/save_cpc_token_lists.ipynb`
    - `input/preprocess-complete-v2/save_patent_wise.ipynb`
    - `input/preprocess-complete-v2/split/gen_leveldb.ipynb`
    - (this step will take at least 2 weeks in my environment)
3. generate DB for publication_number (row id) to token
    - `input/preprocess-all-token-single/save.ipynb`
    - `input/preprocess-all-token-single/gen_leveldb.ipynb`

NOTE:
- To avoid OOM, free memory when each notebook is finished executing.
- The submission notebooks will delete all data in `/kaggle/working` when they are executed.
- Sufficient disk space is required. 
    - At least 2TB is required.
    - If you do not have enough space, please delete unnecessary intermediate files as appropriate.

## Supplemental Information for Competition Organizers
- Dockerfile is used instead of `B4.requirements.txt`.
- `src/config.yaml` is used instead of `B6. SETTINGS.json`.
- There are no `B7. Serialized copy of the trained model`.
- `B8. entry_points.md` is not included because my all codes are `.ipynb` format.

