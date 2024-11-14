# GALOP - Genome Assembly using Long reads Pipeline

This repository contains an exact copy of the standard Genoscope long reads assembly pipeline.

At the moment, this is not intended for users to download as it uses grid submission commands that will only work at Genoscope. As time goes on, we intend to make this pipeline available to a broader audience. However, genome assembly and polishing commands are accessible in the `lib/assembly.py` and `lib/polishing.py` files.

```
galop.py -h
Mandatory arguments:
  --step {assembly,polishing}
                        Defines if the program will launch assembly or polishing scripts (default: None)

Assembly step arguments:
  --proj PROJECT_CODE, -p PROJECT_CODE
                        Project and material codes, can be given multiple times (eg. -p BCM,A,B -p BWW,AB)
                        (default: None)
  -i INPUT_FILE         Nanopore reads fastq file (default: )
  --size GENOME_SIZE, -s GENOME_SIZE
                        Estimated size of the genome in Mb (default: None)
  --cov READSET_COVERAGE, -c READSET_COVERAGE
                        Coverage to use for longest and filtlong subsets (default: 30)
  --assemblers ASSEMBLER_LIST
                        Comma-separated list of assemblers to use (e.g. '--assemblers
                        Smartdenovo,Raven,Wtdbg2'will not launch flye nor Necat. Choices: Flye, Hifiasm, Necat,
                        Nextdenovo, Raven, Shasta,Smartdenovo, Wtdbg2 (default:
                        Smartdenovo,Wtdbg2,Flye,Necat,Nextdenovo)
  --readsets READSET_LIST
                        Comma-separated list of readsets to use (e.g. '--readsets Filtlong,Longest' will not
                        launch assemblies with all reads (default: Full,Filtlong,Longest)
  --no-readset          Disables readset creation (default: False)
  --all-readsets        Disables the use of lsRunProj to check for readset validity and instead use all available
                        readsets (default: False)
  --force               Skips directory creation (default: False)
  --nano-raw            Use --nano-raw instead of --nano-hq in Flye (default: False)
  --pacbio              Look for PacBio runs when building readsets. (default: False)

Polishing step arguments:
  --model MEDAKA_MODEL, -m MEDAKA_MODEL
                        Model to use for medaka polishing (default: r941_prom_sup_g507)
  --pe1 PE1_PATH        Path to the Illumina R1 file (.gz or .fastq) (default: None)
  --pe2 PE2_PATH        Path to the Illumina R2 file (.gz or .fastq) (default: None)
  --assembly ASSEMBLY, -a ASSEMBLY
                        FULL PATH to the assembly to polish (default: )
  --assembly_dir ASSEMBLY_DIR
                        FULL PATH to the directory ouput of the 'nanopore_assembly_pipeline --step assembly'
                        (default: )
  --racon               Enables the racon step (default: False)
  --no_medaka           Skip the medaka step (default: False)

Optional arguments:
  --dir OUTPUT_DIRECTORY, -d OUTPUT_DIRECTORY
                        Output directory (default: None)
  --help, -h            Show this help message and exit

Submission arguments:
  --submode {msub,local}
                        Either submit using ccc_msub or run in local mode (default: msub)
  --nolaunch            Creates submission scripts but does not launch them (default: False)
  --account ACCOUNT     Account to use for submission (default: bistace)
  --qos {long,week,nolimit,xlarge,xxlarge}
                        QoS to use for submission (default: )
  --assembly_queue {normal,xlarge,small,broadwell,xxlarge}
                        Cluster queue to use for the assembly step (default: normal)
  --assembly_core ASSEMBLY_CORE_NUMBER
                        Number of cores to use for the assembly step (default: 36)
  --polishing_queue {normal,xlarge,small,broadwell,xxlarge}
                        Cluster queue to use for the polishing step (default: normal)
  --polishing_core POLISHING_CORE_NUMBER
                        Number of cores to use for the polishing step (default: 36)
  --wait                Wait for all jobs to finish before exiting (default: False)
```
