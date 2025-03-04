import argparse
import os
import sys


def get_args():
    parser = argparse.ArgumentParser(
        prog="GALoP",
        description="\n\nExecutes the standard Genoscope long reads assembly pipeline.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=False,
    )

    commands = parser.add_subparsers(dest="command", required=True)
    assembly_parser = commands.add_parser("assembly")
    polishing_parser = commands.add_parser("polish")

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
    )

    add_optional_arguments(assembly_parser)
    add_optional_arguments(polishing_parser)

    args = parser.parse_args()

    if args.command == "assembly":
        if args.nanopore_input_file is None and args.pacbio_input_file is None:
            print("ERROR: Please provide --nanopore and/or --pacbio", file=sys.stderr)
            sys.exit(1)

        args.nanopore_input_file = abs_path_list(args.nanopore_input_file)
        args.pacbio_input_file = abs_path_list(args.pacbio_input_file)

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


def add_optional_arguments(parser):
    optional_args = parser.add_argument_group("Optional arguments")
    optional_args.add_argument(
        "-p", "--profile",
        action="store",
        dest="config",
        help="Name of a snakemake cluster profile directory",
        default="genoscope",
    )
    optional_args.add_argument(
        "-e", "--executor",
        action="store",
        dest="executor",
        help="Name of a snakemake executor plugin",
        default="slurm",
    )
    optional_args.add_argument(
        "-o", "--output",
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