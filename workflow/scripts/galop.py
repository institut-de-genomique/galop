#!/usr/bin/env python3
from lib import assemblies
from lib import polishing
from lib import checks
from lib import readsets
from lib.config import Config, ReadsetConfig

from slurpy.runner import Runner

import argparse
import os
import sys
import getpass

def create_dir(path, message):
    try:
        os.mkdir(path)
        print(message)
    except FileExistsError:
        print(f"Directory {path} already exists.")
        print("Please remove it or use the --force option to skip directory creation.")
        exit(-1)
    except FileNotFoundError:
        print(f"Path to {path} does not exist.")
        exit(-1)
    except PermissionError:
        print(f"Unsufficient permissions to write output directory {path}")
        exit(-1)


def create_dir_tree(output_dir):
    print("\nCreating directory tree...")

    create_dir(output_dir, f"-- {output_dir}/")
    os.chdir(output_dir)

    create_dir("Reads", "---- Reads/")

    create_dir("Assembly", "---- Assembly/")
    create_dir("Assembly/Smartdenovo", "------ Smartdenovo")
    create_dir("Assembly/Raven", "------ Raven")
    create_dir("Assembly/Wtdbg2", "------ Wtdbg2")
    create_dir("Assembly/Flye", "------ Flye")
    create_dir("Assembly/Hifiasm", "------ Hifiasm")

    create_dir("Submission_scripts", "---- Submission_scripts/")


def create_dir_tree_polishing(output_dir):
    print("\nCreating directory tree...")

    try:
        os.mkdir(output_dir)
    except FileExistsError:
        pass
    except FileNotFoundError:
        print(f"Path to {output_dir} does not exist.")
        exit(-1)
    except PermissionError:
        print(f"Unsufficient permissions to write output directory {output_dir}")
        exit(-1)
    os.chdir(output_dir)

    create_dir("Polishing", "---- Polishing/")
    create_dir("Polishing/Racon", "------ Racon")
    create_dir("Polishing/Medaka", "------ Medaka")
    create_dir("Polishing/Hapog", "------ Hapo-G")

    try:
        os.mkdir("Submission_scripts")
        print("---- Submission_scripts/")
    except FileExistsError:
        pass
    except FileNotFoundError:
        print(f"Path to {output_dir} does not exist.")
        exit(-1)
    except PermissionError:
        print(f"Unsufficient permissions to write output directory Submission_scripts")
        exit(-1)

    

if __name__ == "__main__":
    print("")

    parser = argparse.ArgumentParser(
        prog="nanopore_assembly_pipeline.py",
        description="\n\nExecutes the standard Genoscope Nanopore assembly pipeline.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=False,
    )

    mandatory_args = parser.add_argument_group("Mandatory arguments")
    mandatory_args.add_argument(
        "--step",
        action="store",
        dest="step",
        help="Defines if the program will launch assembly or polishing scripts",
        default=None,
        required=True,
        choices=["assembly", "polishing"],
    )

    assembly_mandatory_args = parser.add_argument_group("Assembly step arguments")
    assembly_mandatory_args.add_argument(
        "--proj",
        "-p",
        action="append",
        dest="project_code",
        help="Project and material codes, can be given multiple times (eg. -p BCM,A,B -p BWW,AB)",
        default=None,
        required=False,
        nargs=1,
    )
    assembly_mandatory_args.add_argument(
        "-i",
        action="store",
        dest="input_file",
        help="Nanopore reads fastq file",
        default="",
        required=False,
    )
    assembly_mandatory_args.add_argument(
        "--size",
        "-s",
        action="store",
        dest="genome_size",
        help="Estimated size of the genome in Mb",
        default=None,
        required=False,
        type=float,
    )
    assembly_mandatory_args.add_argument(
        "--cov",
        "-c",
        action="store",
        dest="readset_coverage",
        help="Coverage to use for longest and filtlong subsets",
        default=30,
        required=False,
        type=int,
    )
    assembly_mandatory_args.add_argument(
        "--assemblers",
        action="store",
        dest="assembler_list",
        help="Comma-separated list of assemblers to use (e.g. '--assemblers Smartdenovo,Raven,Wtdbg2'" 
             "will not launch flye nor Necat. Choices: Flye, Hifiasm, Necat, Nextdenovo, Raven, Shasta," 
             "Smartdenovo, Wtdbg2",
        default="Smartdenovo,Wtdbg2,Flye,Necat,Nextdenovo",
        required=False,
    )
    assembly_mandatory_args.add_argument(
        "--readsets",
        action="store",
        dest="readset_list",
        help="Comma-separated list of readsets to use (e.g. '--readsets Filtlong,Longest' "
             "will not launch assemblies with all reads",
        default="Full,Filtlong,Longest",
        required=False,
    )
    assembly_mandatory_args.add_argument(
        "--no-readset",
        action="store_true",
        dest="no_readset",
        help="Disables readset creation",
        default=False,
        required=False,
    )
    assembly_mandatory_args.add_argument(
        "--all-readsets",
        action="store_true",
        dest="use_all_readsets",
        help="Disables the use of lsRunProj to check for readset validity and instead use all available readsets",
        default=False,
        required=False,
    )
    assembly_mandatory_args.add_argument(
        "--force",
        action="store_true",
        dest="force",
        help="Skips directory creation",
        default=False,
        required=False,
    )
    assembly_mandatory_args.add_argument(
        "--nano-raw",
        action="store_true",
        dest="hq_reads",
        help="Use --nano-raw instead of --nano-hq in Flye",
        default=False,
        required=False,
    )
    assembly_mandatory_args.add_argument(
        "--pacbio",
        action="store_true",
        dest="pacbio",
        help="Look for PacBio runs when building readsets."
    )

    polishing_mandatory_args = parser.add_argument_group("Polishing step arguments")
    polishing_mandatory_args.add_argument(
        "--model",
        "-m",
        action="store",
        dest="medaka_model",
        help="Model to use for medaka polishing",
        default="r941_prom_sup_g507",
        required=False,
    )
    polishing_mandatory_args.add_argument(
        "--pe1",
        action="append",
        dest="pe1_path",
        help="Path to the Illumina R1 file (.gz or .fastq)",
        default=None,
    )
    polishing_mandatory_args.add_argument(
        "--pe2",
        action="append",
        dest="pe2_path",
        help="Path to the Illumina R2 file (.gz or .fastq)",
        default=None,
    )
    polishing_mandatory_args.add_argument(
        "--assembly",
        "-a",
        action="store",
        dest="assembly",
        help="FULL PATH to the assembly to polish",
        default="",
        required=False,
    )
    polishing_mandatory_args.add_argument(
        "--assembly_dir",
        action="store",
        dest="assembly_dir",
        help="FULL PATH to the directory ouput of the 'nanopore_assembly_pipeline --step assembly'",
        default="",
        required=False,
    )
    polishing_mandatory_args.add_argument(
        "--racon",
        action="store_true",
        dest="racon",
        help="Enables the racon step",
        default=False,
        required=False,
    )
    polishing_mandatory_args.add_argument(
        "--no_medaka",
        action="store_true",
        dest="no_medaka",
        help="Skip the medaka step",
        default=False,
        required=False,
    )

    optional_args = parser.add_argument_group("Optional arguments")
    optional_args.add_argument(
        "--dir",
        "-d",
        action="store",
        dest="output_directory",
        help="Output directory",
        default=None,
    )
    optional_args.add_argument(
        "--help", "-h", action="help", help="Show this help message and exit"
    )

    submission_args = parser.add_argument_group("Submission arguments")
    submission_args.add_argument(
        "--submode",
        action="store",
        dest="sub_mode",
        help="Either submit using ccc_msub or run in local mode",
        choices=["msub", "local"],
        default="msub",
    )
    submission_args.add_argument(
        "--nolaunch",
        action="store_true",
        dest="no_launch",
        help="Creates submission scripts but does not launch them",
        default=False,
    )
    submission_args.add_argument(
        "--account",
        action="store",
        dest="account",
        help="Account to use for submission",
        default=getpass.getuser(),
    )
    submission_args.add_argument(
        "--qos",
        action="store",
        dest="qos",
        help="QoS to use for submission",
        choices=["long", "week", "nolimit", "xlarge", "xxlarge"],
        default="",
    )
    submission_args.add_argument(
        "--assembly_queue",
        action="store",
        dest="assembly_queue",
        help="Cluster queue to use for the assembly step",
        choices=["normal", "xlarge", "small", "broadwell", "xxlarge"],
        default="normal",
    )
    submission_args.add_argument(
        "--assembly_core",
        action="store",
        dest="assembly_core_number",
        help="Number of cores to use for the assembly step",
        default=36,
        type=int,
    )
    submission_args.add_argument(
        "--polishing_queue",
        action="store",
        dest="polishing_queue",
        help="Cluster queue to use for the polishing step",
        choices=["normal", "xlarge", "small", "broadwell", "xxlarge"],
        default="normal",
    )
    submission_args.add_argument(
        "--polishing_core",
        action="store",
        dest="polishing_core_number",
        help="Number of cores to use for the polishing step",
        default=36,
        type=int,
    )
    submission_args.add_argument(
        "--wait",
        action="store_true",
        dest="wait",
        help="Wait for all jobs to finish before exiting",
    )

    args = parser.parse_args()
    output_directory = checks.check_output_directory(
        args.step, args.output_directory, args.assembly_dir
    )
    script_path = os.path.abspath(os.path.dirname(sys.argv[0]))
    runner = Runner(
        account=args.account, submission_dir=f"Submission_scripts", verbose=True, no_launch=args.no_launch
    )
    print("%s\n" % (" ".join(sys.argv)))

    checks.check_input_file(args.step, args.input_file, args.force, args.project_code)
    checks.check_assemblers(args.assembler_list)
    checks.check_readsets(args.readset_list)
    checks.check_genome_size(args.step, args.genome_size)
    checks.check_paired_ends(args.step, args.pe1_path, args.pe2_path)
    checks.check_medaka_model(args.step, args.no_medaka, args.medaka_model)

    # By default, time limit is set to 24h
    time_limit = 24 * 60 * 60
    # 3 days
    if args.qos == "long":
        time_limit = 3 * 24 * 60 * 60
    # 1 week
    if args.qos in ["week", "xlarge", "xxlarge"]:
        time_limit = 7 * 24 * 60 * 60

    if args.step == "assembly":
        if not args.force:
            create_dir_tree(output_directory)
        else:
            os.chdir(output_directory)

        if args.input_file == "":
            project_codes = [elt[0].split(",")[0] for elt in args.project_code]
            materials = [elt[0].split(",")[1:] for elt in args.project_code]
        else:
            args.input_file = os.path.abspath(args.input_file)

        total_job, filtlong_job, longest_job = None, None, None
        if not args.no_readset:
            readset_config = ReadsetConfig(
                script_path=script_path, queue=args.assembly_queue, project_codes=args.project_code,
                genome_size=args.genome_size, qos=args.qos, readset_list=args.readset_list,
                coverage=int(args.readset_coverage), use_all_readsets=args.use_all_readsets,
                input_file=args.input_file, pacbio=args.pacbio, wait=args.wait,
            )

            (total_job, filtlong_job, longest_job,) = readsets.launch_readsets_creation(
                runner,
                readset_config
            )

        assemblies.launch_assembly(
            runner,
            script_path,
            output_directory,
            args.assembly_queue,
            args.assembly_core_number,
            args.qos,
            (total_job, filtlong_job, longest_job),
            args.genome_size,
            args.assembler_list,
            args.readset_list,
            not args.hq_reads,
            time_limit,
            args.wait,
        )

    if args.step == "polishing":
        if not args.assembly:
            print("\nFATAL: No assembly was provided")
            exit(1)

        args.assembly = os.path.abspath(args.assembly)
        args.assembly_dir = os.path.abspath(args.assembly_dir)
        
        if not args.force:
            create_dir_tree_polishing(output_directory)
        else:
            os.chdir(output_directory)

        polishing.launch_polishing(
            runner,
            script_path,
            output_directory,
            args.assembly_dir,
            args.polishing_queue,
            args.polishing_core_number,
            args.qos,
            args.racon,
            args.no_medaka,
            args.assembly,
            time_limit,
            args.medaka_model,
            args.pe1_path,
            args.pe2_path,
            args.wait,
        )
