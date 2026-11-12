# Data attribution and reproducible preparation

Reference source: [michaelozon/candidate-matching-synthetic](https://huggingface.co/datasets/michaelozon/candidate-matching-synthetic). Its card declares synthetic data and MIT. A complete standalone copyright/license notice was not retrieved, so raw and processed binaries are not redistributed in this public project. Local files remain untouched and Git-ignored. Dataset terms do not automatically license project code.

The original local download URL/revision was not recorded. The reference source has matching schema/counts; the paths below were inspected in its Files browser. Commands pin a visible upstream revision. Actual shell downloads/byte equivalence could not be tested because network DNS is restricted in the agent shell. Audit downloaded data and compare hashes before claiming exact reproduction.

## macOS

Run from a fresh project clone with its environment active. These commands replace the named raw files; do not overwrite irreplaceable data.

```sh
mkdir -p data/raw data/processed
curl -fL "https://huggingface.co/datasets/michaelozon/candidate-matching-synthetic/resolve/178ab864dcad9910c5670d43e4bdbbb901a11f18/resumes/train-00000-of-00001.parquet" -o data/raw/resumes.parquet
curl -fL "https://huggingface.co/datasets/michaelozon/candidate-matching-synthetic/resolve/178ab864dcad9910c5670d43e4bdbbb901a11f18/jobs/train-00000-of-00001.parquet" -o data/raw/jobs.parquet
curl -fL "https://huggingface.co/datasets/michaelozon/candidate-matching-synthetic/resolve/178ab864dcad9910c5670d43e4bdbbb901a11f18/matches/train-00000-of-00001.parquet" -o data/raw/matches.parquet
python inspect_data.py
python audit_data.py
python preprocess_data.py
python verify_processed.py
```

## Windows Anaconda PowerShell Prompt

```powershell
New-Item -ItemType Directory -Force data/raw, data/processed
Invoke-WebRequest -Uri "https://huggingface.co/datasets/michaelozon/candidate-matching-synthetic/resolve/178ab864dcad9910c5670d43e4bdbbb901a11f18/resumes/train-00000-of-00001.parquet" -OutFile data/raw/resumes.parquet
Invoke-WebRequest -Uri "https://huggingface.co/datasets/michaelozon/candidate-matching-synthetic/resolve/178ab864dcad9910c5670d43e4bdbbb901a11f18/jobs/train-00000-of-00001.parquet" -OutFile data/raw/jobs.parquet
Invoke-WebRequest -Uri "https://huggingface.co/datasets/michaelozon/candidate-matching-synthetic/resolve/178ab864dcad9910c5670d43e4bdbbb901a11f18/matches/train-00000-of-00001.parquet" -OutFile data/raw/matches.parquet
python inspect_data.py
python audit_data.py
python preprocess_data.py
python verify_processed.py
```

Expected raw counts: 10,000 resumes, 2,500 jobs, 2,500 match rows; processed pair count 75,000. Audits should show no missing raw values, duplicate primary IDs/pairs or unknown links. If files/counts differ, rerun evaluation and do not apply stored metrics to different data.

## Preserved local raw SHA-256

```text
4a25add9c3a620c4c396e867063e390fc8084f9b53ed8135def049303a29d7a4  resumes.parquet
c13d7c7e0ab510e81117974027de1364f973a27b3cacc8fabfbd8851c352c871  jobs.parquet
dab24e40948b2da348c6df7072b5b5fe3bb6ef8cab335f88eef5d5667ee79a92  matches.parquet
```

macOS: `shasum -a 256 data/raw/*.parquet`. Windows: `Get-FileHash data/raw/*.parquet -Algorithm SHA256`.
