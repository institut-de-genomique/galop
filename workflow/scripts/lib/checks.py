import os


def check_output_directory(step, output_directory, assembly_dir=""):
    if step == "assembly":
        if output_directory is None:
            return os.path.abspath("./nanopore_assembly")
        else:
            return os.path.abspath(output_directory)
    else:
        if output_directory is None:
            return os.path.abspath(assembly_dir)
        else:
            return os.path.abspath(output_directory)


def check_input_file(step, input_file, force, project_code):
    if step == "assembly":
        if input_file == "" and not force and project_code is None:
            print(
                "FATAL ERROR: You need to either select project codes and materials (--proj) or a single Nanopore fastq file (-i)."
            )
            exit(-1)


def check_assemblers(assembler_list):
    for assembler in assembler_list.split(","):
        if assembler.upper() not in [
            "WTDBG2",
            "SMARTDENOVO",
            "RAVEN",
            "FLYE",
            "NECAT",
            "HIFIASM",
            "NEXTDENOVO",
            "SHASTA",
        ]:
            print(
                "FATAL ERROR: assembler '%s' is not in the list of authorized assemblers."
                % (assembler)
            )
            exit(1)


def check_readsets(readset_list):
    for readset in readset_list.split(","):
        if readset.upper() not in ["FULL", "FILTLONG", "LONGEST"]:
            print(
                "FATAL ERROR: readset '%s' is not in the list of authorized readsets."
                % (readset)
            )
            exit(1)


def check_genome_size(step, genome_size):
    if step == "assembly":
        if genome_size is None:
            print(
                "You need to specify a genome size in Megabases with the --size argument"
            )
            exit(1)


def check_paired_ends(step, pe1_path, pe2_path):
    if step == "polishing" and pe1_path and pe2_path:
        for pe in pe1_path:
            if not os.path.exists(pe):
                print("\nFATAL ERROR: Path to --pe1_path %s doesn't exist." % (pe))
                exit(1)

        for pe in pe2_path:
            if not os.path.exists(pe):
                print("\nFATAL ERROR: Path to --pe2_path %s doesn't exist." % (pe))
                exit(1)


def check_medaka_model(step, no_medaka, model):
    if step == "polishing" and not no_medaka:
        if not model:
            print(
                "\nFATAL: No medaka model was given as input with --medaka_model and -no_medaka was not specified"
            )
