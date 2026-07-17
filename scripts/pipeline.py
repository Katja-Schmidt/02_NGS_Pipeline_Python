#!/usr/bin/env python3

from pathlib import Path
import argparse
import subprocess
import logging
import yaml


# ============================================================
# Logging
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ============================================================
# Load configuration
# ============================================================

def load_config(config_file):

    with open(config_file, "r") as file:
        config = yaml.safe_load(file)

    return config


# ============================================================
# Execute command
# ============================================================

def run_command(command, dry_run=True):

    logger.info("Running command:")
    logger.info(" ".join(command))

    if dry_run:
        logger.info("Dry-run mode enabled.\n")
        return

    subprocess.run(command, check=True)


# ============================================================
# FastQC
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

	logger.info(f"STAR finished for {sample_name}\n")

# ============================================================
# fastp
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

            "-i", sample["R1"],
            "-I", sample["R2"],

            "-o", str(trimmed_r1),
            "-O", str(trimmed_r2),

            "--html", str(html_report),
            "--json", str(json_report)
        ]

        run_command(
            command,
            dry_run=False
        )

# ============================================================
# STAR
# ============================================================

def run_star(config):

    output_dir = Path("results/star")

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    for sample_name, sample in config["samples"].items():

        logger.info(f"========== {sample_name} ==========")

        trimmed_r1 = f"results/fastp/{sample_name}_R1_trimmed.fastq.gz"
        trimmed_r2 = f"results/fastp/{sample_name}_R2_trimmed.fastq.gz"

        prefix = output_dir / sample_name

        command = [

            config["star"],

            "--runThreadN", str(config["threads"]),

            "--genomeDir", config["genomeDir"],

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

# ============================================================
# SAMtools Sort
# ============================================================

def run_samtools_sort(config):

    for sample_name in config["samples"].keys():

        logger.info(f"========== {sample_name} ==========")

        input_bam = f"results/star/{sample_name}_Aligned.sortedByCoord.out.bam"

        output_bam = f"results/star/{sample_name}_sorted.bam"

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

# ============================================================
# SAMtools Index
# ============================================================

def run_samtools_index(config):

    for sample_name in config["samples"].keys():

        logger.info(f"========== {sample_name} ==========")

        bam_file = f"results/star/{sample_name}_sorted.bam"

        command = [

            config["samtools"],

            "index",

            bam_file
        ]

        run_command(
            command,
            dry_run=False
        )

# ============================================================
# featureCounts
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

# ============================================================
# MultiQC
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

    logger.info("MultiQC finished successfully.\n")

# ============================================================
# Main
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

    logger.info("Step 1/7 : FastQC\n")

    run_fastqc(config)

    logger.info("Step 2/7 : fastp\n")

    run_fastp(config)

    logger.info("Step 3/7 : STAR\n")

    run_star(config)
    
    logger.info("Step 4/7 : SAMtools Sort\n")

    run_samtools_sort(config)
    
    logger.info("Step 5/7 : SAMtools Index\n")

    run_samtools_index(config)
    
    logger.info("Step 6/7 : featureCounts\n")

    run_featurecounts(config)
    
    logger.info("Step 7/7 : MultiQC\n")

    run_multiqc(config)

    logger.info("Pipeline finished successfully.")

# ============================================================
# Run
# ============================================================

if __name__ == "__main__":
    main()
