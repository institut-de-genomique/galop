# GALOP - Genome Assembly using Long reads Pipeline

**GALoP** is a Python wrapper around a [Snakemake](https://snakemake.readthedocs.io) workflow, designed to streamline the assembly of genomes using long reads (Nanopore, PacBio) and optionally Hi-C data. It automates read subsetting and assembly with various tools.

## Features

*   **Supported Data Types**:
    *   Oxford Nanopore (ONT)
    *   PacBio HiFi
    *   Hi-C
*   **Read Processing**:
    *   Automatic subsetting (all reads, longest, [filtlong](https://github.com/rrwick/Filtlong)) to optimize assembly results.
    *   Read statistics generation.
*   **Assemblers**:
    *   [Hifiasm](https://github.com/chhylp123/hifiasm) (for PacBio, ONT, and Hybrid assemblies, with optional Hi-C phasing)
    *   [Flye](https://github.com/fenderglass/Flye) (for ONT)
    *   [NextDenovo](https://github.com/Nextomics/NextDenovo) (for ONT and PacBio)
*   **Cluster Integration**: Built-in support for Slurm execution via Snakemake profiles.
*   **Containerization**: Supports execution via Apptainer/Singularity or Docker.

## Installation

### Prerequisites

*   Python 3
*   Snakemake
*   Apptainer or Docker (optional, but recommended)

### Install from Source

Clone the repository and install using `pip`:

```bash
git clone https://github.com/institut-de-genomique/galop
cd galop
pip install .
```

### Basic Usage

**Nanopore Assembly:**

```bash
galop assembly \
    --nanopore reads.fastq.gz \
    --size 100 \
    --output my_assembly_dir
```

**PacBio Assembly:**

```bash
galop assembly \
    --pacbio reads.hifi.fastq.gz \
    --size 100 \
    --output my_assembly_dir
```

**Hybrid Assembly (Nanopore + PacBio, assemblies with a single technology will also be generated):**

```bash
galop assembly \
    --nanopore ont_reads.fastq.gz \
    --pacbio pacbio_reads.fastq.gz \
    --size 100 \
    --output my_assembly_dir
```

**Hi-C Phased Assembly:**

To use Hi-C data for phasing (with Hifiasm):

```bash
galop assembly \
    --pacbio reads.hifi.fastq.gz \
    --hic R1.fastq.gz,R2.fastq.gz \
    --size 100 \
    --output my_phased_assembly
```

**Customizing Readsets and Assemblers:**

You can specify which read subsets and assemblers to run:

```bash
galop assembly \
    --nanopore reads.fastq.gz \
    --size 100 \
    --readsets Full,Filtlong \
    --assemblers Flye,Nextdenovo \
    --cov 40
```

*   `--readsets`: Choose from `Full` (all reads), `Longest`, `Filtlong`.
*   `--assemblers`: Choose from `Hifiasm`, `Nextdenovo`, `Flye`.
*   `--cov`: Target coverage for read subsets (default: 30x).

**Running on a Slurm Cluster:**

To submit jobs to a Slurm cluster:

```bash
galop assembly \
    --nanopore reads.fastq.gz \
    --size 100 \
    --executor slurm
```

**Using Containers:**

To run the pipeline using Apptainer containers use `--use-apptainer`, to use Docker set `--use-docker`:

```bash
galop assembly \
    --nanopore reads.fastq.gz \
    --size 100 \
    --use-apptainer
```

## Arguments Reference

| Argument           | Description                                                                                      |
| :----------------- | :---------------------------------------------------------------------------------------------- |
| `--nanopore`       | Nanopore fastq file(s). Can be specified multiple times.                                        |
| `--pacbio`         | PacBio fastq file(s). Can be specified multiple times.                                          |
| `--hic`            | Hi-C paired-end fastq files as comma-separated pairs (e.g., `R1,R2`). Can be specified multiple times. |
| `--size`, `-s`     | **Required**. Estimated genome size in Mb.                                                      |
| `--output`, `-o`   | Output directory (default: `galop_assembly`).                                                   |
| `--profile`, `-p`  | Snakemake profile name for cluster execution.                                                   |
| `--executor`, `-e` | Snakemake executor (default: `slurm`, can be set to `local` for single machine execution).      |
| `--assemblers`     | List of assemblers to use (default: `Hifiasm,Nextdenovo,Flye`).                                |
| `--readsets`       | List of readsets to generate (default: `Full,Filtlong,Longest`).                               |
| `--cov`, `-c`      | Coverage for subsets (default: 30).                                                             |
| `--use-apptainer`  | Enable Apptainer execution.                                                                     |
| `--use-docker`     | Enable Docker execution.                                                                        |

For a full list of options, run `galop assembly --help`.
