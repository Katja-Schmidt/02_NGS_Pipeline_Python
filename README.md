# RNA-seq NGS Pipeline

A Python-based RNA-seq preprocessing pipeline for quality control, read trimming, genome alignment, read quantification, and quality reporting.

The pipeline automates the main preprocessing steps required before downstream RNA-seq analyses such as differential gene expression analysis.

---

# Features

- Quality assessment with **FastQC**
- Read trimming using **fastp**
- Genome alignment using **STAR**
- BAM processing using **SAMtools**
- Gene-level read counting using **featureCounts**
- Quality summary report generated with **MultiQC**
- Configuration through a YAML file
- Modular Python implementation

---

# Workflow

```
Paired-end FASTQ files
            │
            ▼
        FastQC
            │
            ▼
         fastp
            │
            ▼
          STAR
            │
            ▼
   SAMtools Index
            │
            ▼
     featureCounts
            │
            ▼
         MultiQC
```

---

# Project Structure

```
02_NGS_Pipeline_Python/
│
├── config.yaml
├── pipeline.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── fastq/
│   ├── raw/
│   └── trimmed/
│
├── genome/
│   ├── annotation/
│   ├── reference/
│   └── star_index/
│
├── results/
│   ├── fastqc/
│   ├── fastp/
│   ├── bam/
│   ├── counts/
│   └── multiqc/
│
├── logs/
├── scripts/
└── tests/
```

---

# Requirements

- Python 3.11+
- Ubuntu / Linux (tested using WSL2)
- FastQC
- fastp
- STAR
- SAMtools
- featureCounts (Subread)
- MultiQC

---

# Installation

Clone the repository:

```bash
git clone <repository_url>
cd 02_NGS_Pipeline_Python
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Install the required bioinformatics tools:

- FastQC
- fastp
- STAR
- SAMtools
- featureCounts
- MultiQC

---

# Configuration

Edit the configuration file:

```yaml
threads: 8

genomeDir: genome/star_index

gtf: genome/annotation/gencode.v49.primary_assembly.annotation.gtf

samples:
  sample1:
    R1: data/fastq/SRR11365252_1.fastq
    R2: data/fastq/SRR11365252_2.fastq
```

The pipeline supports multiple paired-end samples defined in `config.yaml`.

---

# Running the Pipeline

Run the complete workflow:

```bash
python3 pipeline.py --config config.yaml
```

---

# Pipeline Steps

The pipeline performs the following operations:

1. FastQC quality assessment
2. Read trimming with fastp
3. Genome alignment using STAR
4. BAM indexing using SAMtools
5. Gene quantification using featureCounts
6. Quality summary with MultiQC

---

# Output

The pipeline generates:

- FastQC reports
- Trimmed FASTQ files
- BAM alignment files
- Gene count table
- MultiQC report

Example output directories:

```
results/
├── fastqc/
├── fastp/
├── bam/
├── counts/
└── multiqc/
```

---

# Tools Used

| Tool | Purpose |
|------|---------|
| FastQC | Read quality assessment |
| fastp | Adapter trimming and filtering |
| STAR | RNA-seq alignment |
| SAMtools | BAM processing |
| featureCounts | Gene quantification |
| MultiQC | Summary quality report |

---

# Future Improvements

Planned improvements include:

- Command-line options for individual pipeline steps
- Automatic checkpoint detection
- Improved logging
- Docker support
- Snakemake / Nextflow implementation
- Support for multiple reference genomes

---

# Author

Katarzyna Zielińska

Bioinformatics Portfolio

2026

Created as part of a Bioinformatics Portfolio project focused on RNA-seq data analysis using Python and Linux.
