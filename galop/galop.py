#!/usr/bin/env python3
import os
import subprocess
import sys

from galop import cli


thisdir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
snakefile_path = os.path.join(thisdir, "workflow", "Snakefile")
profiles_path = os.path.join(thisdir, "workflow", "profile")


def create_dir(path: str):
    try:
        os.mkdir(path)
    except FileExistsError:
        pass
    except FileNotFoundError:
        print(f"Path to {path} does not exist.")
        exit(-1)
    except PermissionError:
        print(f"Unsufficient permissions to write output directory {path}")
        exit(-1)


def generate_snakemake_command(args) -> str:
    cmd = f"snakemake --latency-wait 30 --executor {args.executor} -p "
    
    if args.config:
        cmd += f"--profile {profiles_path}/{args.config} "
    
    if args.use_apptainer:
        cmd += "--use-apptainer "

    if args.command == "assembly":
        cmd += f"--snakefile {snakefile_path} "
        cmd += "--config "
        cmd += f"nanopore_input_file=[{','.join(args.nanopore_input_file)}] "
        cmd += f"pacbio_input_file=[{','.join(args.pacbio_input_file)}] "

        cmd += f"genome_size={args.genome_size} "
        cmd += f"readset_list={args.readset_list} readset_coverage={args.readset_coverage} "
        cmd += f"assemblers_list={args.assemblers_list} "
    
    cmd += f"container_version='{args.container_version}' "
    
    return cmd
        
    

def main():
    args = cli.get_args()

    create_dir(args.output_directory)
    os.chdir(args.output_directory)
    cmd = generate_snakemake_command(args)
    print(f"\n{cmd}\n")
    
    process = subprocess.Popen(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr)
    process.wait()

    sys.exit(0)
