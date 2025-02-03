#!/usr/bin/env python3
import gzip
import os
import sys
from glob import glob
from shutil import copy2, copytree, copyfileobj


def gzip_file(src, dest) -> None:
    with open(src, 'rb') as f_in:
        with gzip.open(dest, 'wb') as f_out:
            copyfileobj(f_in, f_out)


def check_input_dir_path(input_dir) -> None:
    if not os.path.exists(input_dir):
        print(f"{input_dir} does not exist.")
        exit(1)


def clean_reads_dir(input_dir, output_dir) -> None:
    print("\nREADS")
    reads_input_dir = os.path.join(input_dir, "Reads")
    reads_output_dir = os.path.join(output_dir, "Reads")

    if not os.path.exists(reads_input_dir):
        print(f"\t\tWARNING: {reads_input_dir} does not exist")
        return

    os.mkdir(reads_output_dir)

    reads_stats_files = ["full.stats", "longest.stats", "filtlong.stats"]
    for f in reads_stats_files:
        file_full_path = os.path.join(reads_input_dir, f)
        if os.path.exists(file_full_path):
            print(f"\tCOPY: .stats\t{file_full_path}")
            copy2(file_full_path, reads_output_dir)
        else:
            print(f"\t\tWARNING: file {file_full_path} does not exist")


def clean_assembler(assembler, input_dir, output_dir, zip_files) -> None:
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
        print(f"\t\tWARNING: Could not create {assembler} output directory {assembler_output_dir}")

    for f1 in os.listdir(assembler_input_dir):
        f1_full_path = os.path.join(assembler_input_dir, f1)

        if os.path.isdir(f1_full_path):
            outdir_path = os.path.join(assembler_output_dir, os.path.basename(f1))
            os.makedirs(outdir_path)

            for f2 in os.listdir(f1_full_path):
                f2_full_path = os.path.join(f1_full_path, f2)
                if os.path.isfile(f2_full_path):
                    output_path = os.path.join(outdir_path, f2)
                    copy_authorized_assembly_file(f2_full_path, output_path, zip_files)
        else:
            output_path = os.path.join(assembler_output_dir, os.path.basename(f1))
            copy_authorized_assembly_file(f1_full_path, output_path, zip_files) 


def copy_authorized_assembly_file(input_path, output_path, zip_file):
    if input_path.endswith((".fasta", ".fa", ".gfa")):
        extension = input_path.split(".")[-1]
        if not zip_file:
            print(f"\t\tCOPY: {extension}\t{input_path}")
            copy2(input_path, output_path)
        else:
            output_path += ".gz"
            print(f"\t\tGZIP: {extension}\t{input_path}")
            gzip_file(input_path, output_path)


def import_necat_config(input_dir, output_dir) -> None:
    assembly_root_dir = os.path.join(input_dir, "Assembly")
    necat_output_path = os.path.join(output_dir, "Assembly", "Necat")
    config_files = ["config.txt", "reads.txt"]
    for f in config_files:
        if os.path.exists(f):
            file_full_path = os.path.join(assembly_root_dir, f)
            file_output_path = os.path.join(necat_output_path, f)
            print(f"\t\tCOPY: .txt\t{file_full_path}")
            copy2(file_full_path, file_output_path)


def import_necat_corrected_reads(input_dir, output_dir) -> None:
    necat_input_path = os.path.join(input_dir, "Assembly", "Necat", "1-consensus", "cns_final.fasta.gz")
    necat_output_dir = os.path.join(output_dir, "Assembly", "Necat", "corrected_reads.fasta.gz")
    if os.path.exists(necat_input_path):
        os.system(f"cp {necat_input_path} {necat_output_dir}")


def clean_assembly_dir(input_dir, output_dir, zip_files) -> None:
    print("\nASSEMBLY")
    assembler_list = ["Smartdenovo", "Wtdbg2", "Raven", "Flye", "Necat", "Hifiasm", "Nextdenovo"]
    for assembler in assembler_list:
        clean_assembler(assembler, input_dir, output_dir, zip_files)
    import_necat_config(input_dir, output_dir)
    import_necat_corrected_reads(input_dir, output_dir)


def clean_racon(input_dir, output_dir, zip_files):
    print("\tRacon")
    racon_input_dir = os.path.join(input_dir, "Racon")
    racon_output_dir = os.path.join(output_dir, "Racon")

    racon_input_path = os.path.join(racon_input_dir, "racon.fasta")
    if os.path.exists(racon_input_path):
        os.mkdir(racon_output_dir)
        racon_output_path = os.path.join(racon_output_dir, "racon.fasta")
        if not zip_files:
            print(f"\t\tCOPY: .fasta\t{racon_input_path}")
            copy2(racon_input_path, racon_output_path)
        else:
            racon_output_path += ".gz"
            print(f"\t\tGZIP: .fasta\t{racon_input_path}")
            gzip_file(racon_input_path, racon_output_path)
    else:
        print(f"\t\tWARNING: No Racon directory in {input_dir}")
        return


def clean_medaka(input_dir, output_dir, zip_files):
    print("\n\tMedaka")
    medaka_input_dir = os.path.join(input_dir, "Medaka")
    medaka_output_dir = os.path.join(output_dir, "Medaka")

    if not os.path.exists(medaka_input_dir):
        print(f"\t\tWARNING: {medaka_input_dir} does not exist")
        return
    else:
        os.mkdir(medaka_output_dir)

    medaka_input_path = os.path.join(medaka_input_dir, "consensus.fasta")
    if os.path.exists(medaka_input_path):
        medaka_output_path = os.path.join(medaka_output_dir, "medaka.fasta")
        if not zip_files:
            print(f"\t\tCOPY: .fasta\t{medaka_input_path}")
            copy2(medaka_input_path, medaka_output_path)
        else:
            medaka_output_path += ".gz"
            print(f"\t\tGZIP: .fasta\t{medaka_input_path}")
            gzip_file(medaka_input_path, medaka_output_path)

    medaka_gaps_input_path = os.path.join(medaka_input_dir, "consensus.fasta.gaps_in_draft_coords.bed")
    if os.path.exists(medaka_gaps_input_path):
        medaka_gaps_output_path = os.path.join(medaka_output_dir, "medaka.fasta.gaps_in_draft_coords.bed")
        print(f"\t\tCOPY: .bed\t{medaka_gaps_input_path}")
        copy2(medaka_gaps_input_path, medaka_gaps_output_path)


def clean_hapog(input_dir, output_dir):
    print("\n\tHapo-g")
    if not os.path.exists(os.path.join(input_dir, "Hapog")):
        print(f"\t\tWARNING: No Hapog directory in {input_dir}")
        return

    directories_to_save = ["cmds", "hapog_results", "logs"]
    for i in range(1, 3):
        hapog_input_dir = os.path.join(input_dir, "Hapog", f"hapog_{i}")
        if os.path.exists(hapog_input_dir):
            hapog_output_dir = os.path.join(output_dir, "Hapog", f"hapog_{i}")
            os.makedirs(hapog_output_dir)

            correspondance_file = os.path.join(hapog_input_dir, "correspondance.txt")
            if os.path.exists(correspondance_file):
                print(f"\t\tCOPY: .txt\t{correspondance_file}")
                copy2(correspondance_file, hapog_output_dir)

            for d in directories_to_save:
                hapog_input_path = os.path.join(hapog_input_dir, d)
                if os.path.exists(hapog_input_path):
                    print(f"\t\tCOPY: DIR\t{hapog_input_path}")
                    hapog_output_path = os.path.join(hapog_output_dir, d)
                    copytree(hapog_input_path, hapog_output_path)
                else:
                    print(f"WARNING: {hapog_input_path} does not exist")


def clean_polishing_dir(input_dir, output_dir, zip_files):
    print("\nPOLISHING")
    polishing_input_dir = os.path.join(input_dir, "Polishing")
    polishing_output_dir = os.path.join(output_dir, "Polishing")

    if not os.path.exists(polishing_input_dir):
        print(f"WARNING: {output_dir} does not exist")
        return

    os.mkdir(polishing_output_dir)

    clean_racon(polishing_input_dir, polishing_output_dir, zip_files)
    clean_medaka(polishing_input_dir, polishing_output_dir, zip_files)
    clean_hapog(polishing_input_dir, polishing_output_dir)


def clean_submission_scripts(input_dir, output_dir):
    print("\nSUBMISSION SCRIPTS")
    input_dir = os.path.join(input_dir, "Submission_scripts")
    output_dir = os.path.join(output_dir, "Submission_scripts")

    if not os.path.exists(input_dir):
        print(f"WARNING: {input_dir} does not exist")
        return

    print(f"\tCOPY: DIR\t{input_dir}")
    copytree(input_dir, output_dir)


def copy_small_files(input_dir, output_dir):
    print("SMALL FILES")
    for root, directorys, files in os.walk(input_dir):
        base_root = root
        root = root.replace(input_dir, "")

        for d in directorys:
            dir_name = output_dir + root + "/" + d
            if not os.path.exists(dir_name):
                os.mkdir(dir_name)

        for f in files:
                input_file_full_path = os.path.join(base_root, f)

                # Save all files weighting less than 20MB
                if os.path.getsize(input_file_full_path) < 20000000:
                    destination = output_dir + root + "/" +  f
                    if not os.path.exists(destination):
                        print(f"\tCOPY:\t {input_file_full_path}")
                        copy2(os.path.join(base_root, f), destination)


def clean(input_dir, output_dir, zip_files) -> None:
    input_dir = os.path.abspath(input_dir)
    check_input_dir_path(input_dir)

    output_dir = os.path.abspath(output_dir)
    try:
        os.mkdir(output_dir)
    except:
        print(f"WARNING: Could not create output directory {output_dir}")
        print(f"If {output_dir} already exists, please remove it before launching the cleaning step.")
        return

    clean_reads_dir(input_dir, output_dir)
    clean_assembly_dir(input_dir, output_dir, zip_files)
    clean_polishing_dir(input_dir, output_dir, zip_files)
    clean_submission_scripts(input_dir, output_dir)
    copy_small_files(input_dir, output_dir)

    print()


def help():
    print(
        "\nCopies files obtained with nanopore_assembly_pipeline to a destination folder and only keeps important files (to save it in a scratch dir, as an example)")
    print("Usage: galop_cleaner.py -i source -o destination\n")
    print("Use option '--zip' to zip fasta files instead of just copying.")
    exit()


if __name__ == "__main__":
    if "-h" in sys.argv:
        help()

    if "-i" not in sys.argv or "-o" not in sys.argv:
        print("You have to specify -i and -o options")
        help()

    input_dir = sys.argv[sys.argv.index("-i") + 1]
    output_dir = sys.argv[sys.argv.index("-o") + 1]

    zip_files = False
    if "--zip" in sys.argv:
        zip_files = True

    clean(input_dir, output_dir, zip_files)
