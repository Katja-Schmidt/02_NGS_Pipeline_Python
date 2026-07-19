#!/usr/bin/env python3

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
# This project presents an automated RNA-seq analysis
# pipeline implemented in Python.
#
# The pipeline performs preprocessing, genome alignment,
# read quantification and quality control for paired-end
# RNA sequencing data.
#
# The analysis includes:
# - Quality control (FastQC)
# - Adapter clipping
# - Quality trimming
# - Read filtering
# - Genome alignment (STAR)
# - BAM sorting
# - BAM indexing
# - Gene quantification (featureCounts)
# - MultiQC summary report
# ============================================================

from pathlib import Path
import argparse
import subprocess
import logging
import yaml

# ============================================================
# 1. Configure Logging
# ============================================================
#
# Configure logging to display pipeline progress,
# executed commands and status messages.
#

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# ============================================================
# 2. Load Configuration File
# ============================================================
#
# Load pipeline settings from a YAML configuration file.
#
# The configuration file contains:
# - software paths
# - sample information
# - genome reference
# - annotation file
# - number of CPU threads
#

def load_config(config_file):

    with open(config_file, "r") as file:
        config = yaml.safe_load(file)

    return config

# ============================================================
# 3. Execute External Command
# ============================================================
#
# Execute a command-line program from Python.
#
# Each executed command is written to the log.
# Dry-run mode allows verification without execution.
#

def run_command(command, dry_run=True):

    logger.info("Running command:")
    logger.info(" ".join(command))

    if dry_run:
        logger.info("Dry-run mode enabled.\n")
        return

    subprocess.run(command, check=True)
	
# ============================================================
# 4. Quality Control of Raw Reads (FastQC)
# ============================================================
#
# Evaluate the quality of raw paired-end RNA-seq reads.
#
# FastQC provides an initial assessment of sequencing
# quality before any preprocessing steps.
#
# The generated reports include:
# - Per base sequence quality
# - GC content
# - Sequence duplication levels
# - Adapter contamination
# - Overrepresented sequences
#
# Reports are saved to:
# results/fastqc/
# ============================================================

def run_fastqc(config):

    output_dir = Path("results/fastqc")

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    for sample_name, sample in config["samples"].items():

        logger.info(f"========== {sample_name} ==========")

        command = [

            config["fastqc"],

            sample["R1"],
            sample["R2"],

            "-o",
            str(output_dir)

        ]

        run_command(
            command,
            dry_run=False
        )

    logger.info("FastQC completed successfully.\n")

# ============================================================
# 5. Adapter Clipping, Quality Trimming and Read Filtering
# ============================================================
#
# Preprocess paired-end RNA-seq reads using fastp.
#
# This step performs:
#
# - Adapter removal
# - Quality trimming
# - Read filtering
#
# Trimmed reads are used for downstream genome
# alignment.
#
# HTML and JSON quality reports are generated for
# each sample.
#
# Output directory:
# results/fastp/
# ============================================================

def run_fastp(config):

    output_dir = Path("results/fastp")

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    for sample_name, sample in config["samples"].items():

        logger.info(f"========== {sample_name} ==========")

        trimmed_r1 = output_dir / f"{sample_name}_R1_trimmed.fastq.gz"
        trimmed_r2 = output_dir / f"{sample_name}_R2_trimmed.fastq.gz"

        html_report = output_dir / f"{sample_name}.html"
        json_report = output_dir / f"{sample_name}.json"

        command = [

            config["fastp"],

            "-i",
            sample["R1"],

            "-I",
            sample["R2"],

            "-o",
            str(trimmed_r1),

            "-O",
            str(trimmed_r2),

            "--html",
            str(html_report),

            "--json",
            str(json_report)

        ]

        run_command(
            command,
            dry_run=False
        )

    logger.info("fastp completed successfully.\n")

# ============================================================
# 6. Genome Alignment (STAR)
# ============================================================
#
# Align trimmed paired-end RNA-seq reads to the
# reference genome using the STAR aligner.
#
# STAR produces a coordinate-sorted BAM file,
# which serves as the input for downstream analyses.
#
# Parameters:
# - Multi-threaded execution
# - On-the-fly decompression (zcat)
# - Temporary working directory
# - Coordinate-sorted BAM output
#
# Output directory:
# results/star/
# ============================================================

def run_star(config):

    output_dir = Path("results/star")

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    for sample_name, sample in config["samples"].items():

        logger.info(f"========== {sample_name} ==========")

        trimmed_r1 = (
            f"results/fastp/{sample_name}_R1_trimmed.fastq.gz"
        )

        trimmed_r2 = (
            f"results/fastp/{sample_name}_R2_trimmed.fastq.gz"
        )

        prefix = output_dir / sample_name

        command = [

            config["star"],

            "--runThreadN",
            str(config["threads"]),

            "--genomeDir",
            config["genomeDir"],

            "--readFilesIn",
            trimmed_r1,
            trimmed_r2,

            "--readFilesCommand",
            "zcat",

            "--outTmpDir",
            f"/tmp/{sample_name}_STARtmp",

            "--outSAMtype",
            "BAM",
            "SortedByCoordinate",

            "--outFileNamePrefix",
            str(prefix) + "_"

        ]

        run_command(
            command,
            dry_run=False
        )

    logger.info("STAR alignment completed successfully.\n")

# ============================================================
# 7. BAM Sorting (SAMtools)
# ============================================================
#
# Sort aligned reads according to genomic coordinates.
#
# Coordinate-sorted BAM files improve compatibility
# with downstream RNA-seq tools and visualization
# software.
#
# Output:
# *_sorted.bam
# ============================================================

def run_samtools_sort(config):

    for sample_name in config["samples"].keys():

        logger.info(f"========== {sample_name} ==========")

        input_bam = (
            f"results/star/{sample_name}_Aligned.sortedByCoord.out.bam"
        )

        output_bam = (
            f"results/star/{sample_name}_sorted.bam"
        )

        command = [

            config["samtools"],

            "sort",

            "-o",
            output_bam,

            input_bam

        ]

        run_command(
            command,
            dry_run=False
        )

    logger.info("BAM sorting completed successfully.\n")

# ============================================================
# 8. BAM Indexing (SAMtools)
# ============================================================
#
# Create an index (.bai) for every sorted BAM file.
#
# BAM indexing enables rapid access to genomic
# regions without scanning the complete alignment
# file.
#
# Output:
# *_sorted.bam.bai
# ============================================================

def run_samtools_index(config):

    for sample_name in config["samples"].keys():

        logger.info(f"========== {sample_name} ==========")

        bam_file = (
            f"results/star/{sample_name}_sorted.bam"
        )

        command = [

            config["samtools"],

            "index",

            bam_file

        ]

        run_command(
            command,
            dry_run=False
        )

    logger.info("BAM indexing completed successfully.\n")

# ============================================================
# 9. Gene Quantification (featureCounts)
# ============================================================
#
# Quantify gene expression by assigning aligned reads
# to annotated genomic features.
#
# featureCounts generates a read count matrix that can
# be used as input for downstream differential gene
# expression analysis (e.g. DESeq2 or edgeR).
#
# Parameters:
# - Multi-threaded execution
# - Paired-end read counting
# - GTF gene annotation
#
# Output:
# results/counts.txt
# ============================================================

def run_featurecounts(config):

    output_file = "results/counts.txt"

    bam_files = []

    for sample_name in config["samples"].keys():

        bam_files.append(
            f"results/star/{sample_name}_sorted.bam"
        )

    command = [

        config["featurecounts"],

        "-T",
        str(config["threads"]),

        "-p",

        "-a",
        config["gtf"],

        "-o",
        output_file

    ] + bam_files

    run_command(
        command,
        dry_run=False
    )

    logger.info("featureCounts completed successfully.\n")

# ============================================================
# 10. MultiQC Summary Report
# ============================================================
#
# Aggregate all quality control reports generated
# throughout the pipeline into a single interactive
# HTML report.
#
# MultiQC summarizes results from:
# - FastQC
# - fastp
# - STAR
#
# Output:
# results/multiqc/
# ============================================================

def run_multiqc(config):

    command = [

        config["multiqc"],

        "results",

        "-o",

        "results/multiqc"

    ]

    run_command(
        command,
        dry_run=False
    )

    logger.info("MultiQC report generated successfully.\n")

# ============================================================
# 11. Main Pipeline
# ============================================================
#
# Load configuration and execute every analysis step
# in the correct order.
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description="RNA-seq NGS Pipeline"
    )

    parser.add_argument(
        "--config",
        required=True,
        help="Path to configuration YAML file"
    )

    args = parser.parse_args()

    logger.info("Loading configuration...")

    config = load_config(args.config)

    logger.info("Configuration loaded successfully.\n")

    logger.info("=" * 60)
    logger.info("Starting RNA-seq Pipeline")
    logger.info("=" * 60)

    logger.info("Step 1/7 : FastQC")
    run_fastqc(config)

    logger.info("Step 2/7 : fastp")
    run_fastp(config)

    logger.info("Step 3/7 : STAR")
    run_star(config)

    logger.info("Step 4/7 : SAMtools Sort")
    run_samtools_sort(config)

    logger.info("Step 5/7 : SAMtools Index")
    run_samtools_index(config)

    logger.info("Step 6/7 : featureCounts")
    run_featurecounts(config)

    logger.info("Step 7/7 : MultiQC")
    run_multiqc(config)

    logger.info("=" * 60)
    logger.info("RNA-seq Pipeline completed successfully.")
    logger.info("=" * 60)

# ============================================================
# 12. Run Pipeline
# ============================================================

if __name__ == "__main__":
    main()
