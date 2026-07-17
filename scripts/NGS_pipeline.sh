# ============================================================
# Project:
# RNA-seq Next-Generation Sequencing (NGS) Pipeline
#
# Organism:
# Homo sapiens
#
# Author:
# Katarzyna Zielińska
#
# Date:
# July 2026
#
# Description:
# This script performs preprocessing and alignment of
# paired-end RNA-seq reads.
#
# The analysis includes:
# - Quality control (FastQC)
# - Adapter clipping
# - Quality trimming
# - Read filtering
# - Genome alignment (STAR)
# ============================================================

set -e

# ============================================================
# 1. Define input files
# ============================================================

R1="data/raw/sample_R1.fastq.gz"
R2="data/raw/sample_R2.fastq.gz"

THREADS=8

GENOME="genome/star_index"

# ============================================================
# 2. Create output directories
# ============================================================

mkdir -p results/fastqc_raw
mkdir -p results/fastp
mkdir -p results/fastqc_trimmed
mkdir -p results/bam

# ============================================================
# 3. Quality Control of Raw Reads (FastQC)
# ============================================================
#
# Evaluate sequencing quality before preprocessing.
#

echo "Running FastQC on raw reads..."

fastqc \
    "$R1" \
    "$R2" \
    --threads $THREADS \
    --outdir results/fastqc_raw

# ============================================================
# 4. Adapter Clipping, Quality Trimming and Read Filtering
# ============================================================
#
# Adapter clipping:
# Remove sequencing adapters.
#
# Quality trimming:
# Trim low-quality bases from read ends.
#
# Read filtering:
# Remove reads that are too short or fail quality criteria.
#

echo "Running fastp..."

fastp \
    --in1 "$R1" \
    --in2 "$R2" \
    --out1 data/trimmed/sample_trimmed_R1.fastq.gz \
    --out2 data/trimmed/sample_trimmed_R2.fastq.gz \
    --detect_adapter_for_pe \
    --cut_front \
    --cut_tail \
    --cut_window_size 4 \
    --cut_mean_quality 20 \
    --length_required 30 \
    --thread $THREADS \
    --html results/fastp/fastp_report.html \
    --json results/fastp/fastp_report.json

# ============================================================
# 5. Quality Control of Trimmed Reads (FastQC)
# ============================================================
#
# Evaluate read quality after preprocessing.
#

echo "Running FastQC on trimmed reads..."

fastqc \
    data/trimmed/sample_trimmed_R1.fastq.gz \
    data/trimmed/sample_trimmed_R2.fastq.gz \
    --threads $THREADS \
    --outdir results/fastqc_trimmed

# ============================================================
# 6. Genome Alignment (STAR)
# ============================================================
#
# Align trimmed RNA-seq reads to the reference genome.
#

echo "Running STAR alignment..."

STAR \
    --runThreadN $THREADS \
    --genomeDir "$GENOME" \
    --readFilesIn \
    data/trimmed/sample_trimmed_R1.fastq.gz \
    data/trimmed/sample_trimmed_R2.fastq.gz \
    --readFilesCommand zcat \
    --outSAMtype BAM SortedByCoordinate \
    --outFileNamePrefix results/bam/sample_

# ============================================================
# 7. Pipeline completed
# ============================================================

echo "======================================"
echo "RNA-seq preprocessing completed."
echo "Output directories:"
echo " - results/fastqc_raw"
echo " - results/fastp"
echo " - results/fastqc_trimmed"
echo " - results/bam"
echo "======================================"
