import argparse
import os
import sys

AUTHORIZED_READSETS = ["Full", "Longest", "Filtlong"]
AUTHORIZED_ASSEMBLERS = ["Hifiasm", "Nextdenovo", "Flye"]


def get_args():
    parser = argparse.ArgumentParser(
        prog="GALoP",
        description="\n\nExecutes the standard Genoscope long reads assembly pipeline.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=True,
    )

    commands = parser.add_subparsers(dest="command", required=True)
    assembly_parser = commands.add_parser("assembly")
    commands.add_parser(
        "list-profiles",
        help="List available Snakemake profiles",
    )

    assembly_parser.add_argument(
        "--nanopore",
        action="append",
        dest="nanopore_input_file",
        help="Nanopore fastq file(s). Can be given multiple times or separated by commas (,)",
        required=False,
        default=[],
    )
    assembly_parser.add_argument(
        "--pacbio",
        action="append",
        dest="pacbio_input_file",
        help="PacBio fastq file(s). Can be given multiple times or separated by commas (,)",
        required=False,
        default=[],
    )
    assembly_parser.add_argument(
        "--hic",
        action="append",
        dest="hic_read_pairs",
        help=(
            "Hi-C paired-end fastq files as comma-separated pairs. "
            "Example: --hic R1_1.fastq.gz,R2_1.fastq.gz --hic R1_2.fastq.gz,R2_2.fastq.gz"
        ),
        required=False,
        default=[],
    )
    assembly_parser.add_argument(
        "--size",
        "-s",
        action="store",
        dest="genome_size",
        help="Estimated size of the genome in Mb",
        default=None,
        required=True,
        type=int,
    )
    assembly_parser.add_argument(
        "--cov",
        "-c",
        action="store",
        dest="readset_coverage",
        help="Coverage to use for longest and filtlong subsets",
        default=30,
        required=False,
        type=int,
    )
    assembly_parser.add_argument(
        "--readsets",
        action="store",
        dest="readset_list",
        help="Comma-separated list of readsets to use (e.g. '--readsets Filtlong,Longest' "
        "will not launch assemblies with all reads",
        default="Full,Filtlong,Longest",
        required=False,
        type=check_readset_list,
    )
    assembly_parser.add_argument(
        "--assemblers",
        action="store",
        dest="assemblers_list",
        help="Comma-separated list of assemblers to use (e.g. '--assemblers Hifiasm,Flye'"
        "will not launch Nextdenovo. Choices: Flye, Hifiasm, Nextdenovo",
        default="Hifiasm,Nextdenovo,Flye",
        required=False,
        type=check_assemblers_list,
    )
    assembly_parser.add_argument(
        "--hic-only",
        action="store_true",
        dest="hic_only",
        help="Only launch assemblies with Hi-C data",
        default=False,
        required=False,
    )

    add_optional_arguments(assembly_parser)

    args = parser.parse_args()

    if args.command == "assembly":
        if args.nanopore_input_file is None and args.pacbio_input_file is None:
            print("ERROR: Please provide --nanopore and/or --pacbio", file=sys.stderr)
            sys.exit(1)

        args.nanopore_input_file = abs_path_list(args.nanopore_input_file)
        args.pacbio_input_file = abs_path_list(args.pacbio_input_file)

        # Parse and validate Hi-C pairs if provided
        hic_r1, hic_r2 = parse_hic_pairs(args.hic_read_pairs)
        args.hic_r1 = hic_r1
        args.hic_r2 = hic_r2

    return args


def abs_path_list(paths: list[str]):
    # Used to convert a path [p1, p2, p3, ...] or
    # a str containing paths separated by commas p1,p2,p3,...
    # to a list of absolute paths

    if len(paths) == 0:
        return []

    path_list = []
    for p in paths:
        if "," in p:
            path_list.extend(p.split(","))
        else:
            path_list.append(p)

    abs_paths = []
    for p in path_list:
        abs_paths.append(os.path.abspath(p))
    return abs_paths


def parse_hic_pairs(pairs: list[str]):
    # Convert a list like ["R1a,R2a", "R1b,R2b", ...] to two lists
    # of absolute paths while validating existence.
    if not pairs:
        return [], []

    r1_list = []
    r2_list = []
    for entry in pairs:
        parts = entry.split(",")
        if len(parts) != 2 or not parts[0] or not parts[1]:
            print(
                "ERROR: --hic expects comma-separated pairs: R1.fastq.gz,R2.fastq.gz",
                file=sys.stderr,
            )
            sys.exit(1)
        r1 = os.path.abspath(parts[0])
        r2 = os.path.abspath(parts[1])
        if not os.path.exists(r1):
            print(
                f"ERROR: Hi-C read file not found: {parts[0]} -> {r1}", file=sys.stderr
            )
            sys.exit(1)
        if not os.path.exists(r2):
            print(
                f"ERROR: Hi-C read file not found: {parts[1]} -> {r2}", file=sys.stderr
            )
            sys.exit(1)
        r1_list.append(r1)
        r2_list.append(r2)
    return r1_list, r2_list


def add_optional_arguments(parser):
    optional_args = parser.add_argument_group("Optional arguments")
    optional_args.add_argument(
        "-p",
        "--profile",
        action="store",
        dest="config",
        help="Name of a snakemake cluster profile directory",
        default=None,
    )
    optional_args.add_argument(
        "-e",
        "--executor",
        action="store",
        dest="executor",
        help="Name of a snakemake executor plugin",
        default="slurm",
    )
    optional_args.add_argument(
        "-o",
        "--output",
        action="store",
        dest="output_directory",
        help="Output directory",
        default="galop_assembly",
    )
    optional_args.add_argument(
        "--use-apptainer",
        action="store_true",
        dest="use_apptainer",
        help="Use apptainer to run the pipeline",
        default=False,
    )
    optional_args.add_argument(
        "--container-version",
        action="store",
        dest="container_version",
        help="Container version to use",
        default="0.5",
    )


def check_readset_list(readsets: str):
    authorized_readset = [readset.upper() for readset in AUTHORIZED_READSETS]
    readset_list = readsets.upper().split(",")

    for readset in readset_list:
        if readset not in authorized_readset:
            error_msg = (
                f"ERROR: the '{readset}' readset does not belong to the list "
                f"of authorized readsets. Authorized readsets: {AUTHORIZED_READSETS}"
            )
            print(error_msg, file=sys.stderr)
            sys.exit(1)

    return ",".join(readset_list)


def check_assemblers_list(assemblers: str):
    authorized_assemblers = [assembler.upper() for assembler in AUTHORIZED_ASSEMBLERS]
    assemblers_list = assemblers.upper().split(",")

    for assembler in assemblers_list:
        if assembler not in authorized_assemblers:
            error_msg = (
                f"ERROR: the '{assembler}' assembler does not belong to the list "
                f"of authorized assemblers. Authorized assemblers: {AUTHORIZED_ASSEMBLERS}"
            )
            print(error_msg, file=sys.stderr)
            sys.exit(1)

    return ",".join(assemblers_list)
