import os
import sys
from shutil import copy2
from glob import glob


def check_input_dir_path(input_dir) -> None:
    if not os.path.exists(input_dir):
        print(f"{input_dir} does not exist.")
        exit(1)


def clean_reads_dir(input_dir, output_dir) -> None:
    print("\nREADS")
    reads_input_dir = os.path.join(input_dir, "Reads")
    reads_output_dir = os.path.join(output_dir, "Reads")

    if not os.path.exists(reads_input_dir):
        print(f"WARNING: {reads_input_dir} does not exist")
        return

    os.mkdir(reads_output_dir)

    reads_stats_files = ["nanopore.stats", "longest.stats", "filtlong.stats"]
    for f in reads_stats_files:
        file_full_path = os.path.join(reads_input_dir, f)
        if os.path.exists(file_full_path):
            print(f"\tCOPY: .stats\t{file_full_path}")
            copy2(file_full_path, reads_output_dir)
        else:
            print(f"WARNING: file {file_full_path} does not exist")


def clean_assembler(assembler, input_dir, output_dir) -> None:
    assembler_input_dir = os.path.join(input_dir, "Assembly", assembler)
    assembler_output_dir = os.path.join(output_dir, "Assembly", assembler)

    if os.path.exists(assembler_input_dir):
        if len(os.listdir(assembler_input_dir)) != 0:
            print(f"\t{assembler}")
        else:
            return
    else:
        return

    try:
        os.makedirs(assembler_output_dir)
    except:
        print(
            f"WARNING: Could not create {assembler} output directory {assembler_output_dir}"
        )

    authorized_extensions = [".fasta", ".fa", ".stats"]
    for extension in authorized_extensions:
        for f in glob(f"{assembler_input_dir}/*{extension}"):
            file_full_path = os.path.join(assembler_input_dir, os.path.basename(f))
            print(f"\t\tCOPY: {extension}\t{file_full_path}")
            copy2(file_full_path, assembler_output_dir)


def import_necat_config(input_dir, output_dir) -> None:
    assembly_root_dir = os.path.join(input_dir, "Assembly")
    necat_output_path = os.path.join(output_dir, "Assembly", "Necat")
    config_files = ["config.txt", "reads.txt"]
    for f in config_files:
        if os.path.exists(f):
            file_full_path = os.path.join(assembly_root_dir, f)
            file_output_path = os.path.join(necat_output_path, f)
            copy2(file_full_path, file_output_path)


def clean_assembly_dir(input_dir, output_dir) -> None:
    print("\nASSEMBLY")
    assembler_list = ["Smartdenovo", "Wtdbg2", "Raven", "Flye", "Necat"]
    for assembler in assembler_list:
        clean_assembler(assembler, input_dir, output_dir)
        print()
    import_necat_config(input_dir, output_dir)


def clean_racon(input_dir, output_dir):
    print("\tRacon")
    racon_input_dir = os.path.join(input_dir, "Racon")
    racon_output_dir = os.path.join(output_dir, "Racon")

    racon_input_path = os.path.join(racon_input_dir, "racon.fasta")
    if os.path.exists(racon_input_path):
        os.mkdir(racon_output_dir)
        racon_output_path = os.path.join(racon_output_dir, "racon.fasta")
        print(f"\t\tCOPY: .fasta\t{racon_output_path}")
        copy2(racon_input_path, racon_output_path)


def clean_medaka(input_dir, output_dir):
    print("\n\tMedaka")
    medaka_input_dir = os.path.join(input_dir, "Medaka")
    medaka_output_dir = os.path.join(output_dir, "Medaka")

    if not os.path.exists(medaka_input_dir):
        print(f"WARNING: {medaka_output_dir} does not exist")
        return
    else:
        os.mkdir(medaka_output_dir)

    medaka_input_path = os.path.join(medaka_input_dir, "consensus.fasta")
    if os.path.exists(medaka_input_path):
        medaka_output_path = os.path.join(medaka_output_dir, "medaka.fasta")
        print(f"\t\tCOPY: .fasta\t{medaka_output_path}")
        copy2(medaka_input_path, medaka_output_path)

    medaka_gaps_input_path = os.path.join(
        medaka_input_dir, "consensus.fasta.gaps_in_draft_coords.bed"
    )
    if os.path.exists(medaka_gaps_input_path):
        medaka_gaps_output_path = os.path.join(
            medaka_output_dir, "medaka.fasta.gaps_in_draft_coords.bed"
        )
        print(f"\t\tCOPY .bed\t{medaka_gaps_output_path}")
        copy2(medaka_gaps_input_path, medaka_gaps_output_path)


def clean_polishing_dir(input_dir, output_dir):
    print("\nPOLISHING")
    polishing_input_dir = os.path.join(input_dir, "Polishing")
    polishing_output_dir = os.path.join(output_dir, "Polishing")

    if not os.path.exists(polishing_input_dir):
        print(f"WARNING: {output_dir} does not exist")
        return

    os.mkdir(polishing_output_dir)

    clean_racon(polishing_input_dir, polishing_output_dir)
    clean_medaka(polishing_input_dir, polishing_output_dir)


def clean_submission_scripts(input_dir, output_dir):
    print("\nSUBMISSION SCRIPTS")
    input_dir = os.path.join(input_dir, "Submission_scripts")
    output_dir = os.path.join(output_dir, "Submission_scripts")

    if not os.path.exists(input_dir):
        print(f"WARNING: {input_dir} does not exist")
        return

    os.mkdir(output_dir)

    print("\tCOPY: everything inside")
    for f in glob(f"{input_dir}/*"):
        copy2(f, output_dir)


def clean(input_dir, output_dir) -> None:
    input_dir = os.path.abspath(input_dir)
    check_input_dir_path(input_dir)

    output_dir = os.path.abspath(output_dir)
    try:
        os.mkdir(output_dir)
    except:
        print(f"WARNING: Could not create output directory {output_dir}")

    if input_dir == output_dir:
        print("ERROR: input and output directories must be different")
        exit(1)

    clean_reads_dir(input_dir, output_dir)
    clean_assembly_dir(input_dir, output_dir)
    clean_polishing_dir(input_dir, output_dir)
    clean_submission_scripts(input_dir, output_dir)

    print()


clean(sys.argv[1], sys.argv[2])
