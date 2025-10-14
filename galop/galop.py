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

        cmd += f"hic_r1=[{','.join(args.hic_r1)}] "
        cmd += f"hic_r2=[{','.join(args.hic_r2)}] "

        cmd += f"genome_size={args.genome_size} "
        cmd += f"readset_list={args.readset_list} readset_coverage={args.readset_coverage} "
        cmd += f"assemblers_list={args.assemblers_list} "
    
    cmd += f"container_version='{args.container_version}' "
    
    return cmd
        
    

def main():
    args = cli.get_args()

    # List available Snakemake profiles and exit
    if args.command == "list-profiles":
        print_profiles()
        sys.exit(0)

    create_dir(args.output_directory)
    os.chdir(args.output_directory)
    cmd = generate_snakemake_command(args)
    print(f"\n{cmd}\n")
    
    process = subprocess.Popen(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr)
    process.wait()

    sys.exit(0)


def print_profiles():
    try:
        names = [
            d for d in os.listdir(profiles_path)
            if os.path.isdir(os.path.join(profiles_path, d))
        ]
    except FileNotFoundError:
        print("No profiles directory found.")
        return

    if not names:
        print("No profiles available.")
        return

    rows = []
    for name in sorted(names):
        cfg_path = os.path.join(profiles_path, name, "config.yaml")
        # Defaults
        defaults = {
            "partition": "-",
            "qos": "-",
            "runtime": "-",
            "mem_mb_per_cpu": "-",
        }
        if os.path.exists(cfg_path):
            try:
                with open(cfg_path, "r", encoding="utf-8") as fh:
                    in_default = False
                    for raw in fh:
                        line = raw.rstrip("\n")
                        stripped = line.strip()
                        if not stripped or stripped.startswith("#"):
                            continue
                        if stripped.startswith("default-resources:"):
                            in_default = True
                            continue
                        # Exit default-resources block if we hit another top-level key
                        if in_default and not line.startswith(" "):
                            in_default = False
                        if not in_default:
                            continue
                        # Expect indented key: value
                        if ":" in stripped:
                            k, v = stripped.split(":", 1)
                            k = k.strip()
                            v = v.strip()
                            if k in defaults:
                                defaults[k] = v
            except Exception:
                pass
        rel_path = os.path.join("workflow", "profile", name)
        rows.append([
            name,
            defaults["partition"],
            defaults["qos"],
            defaults["runtime"],
            defaults["mem_mb_per_cpu"],
            rel_path,
        ])

    headers = ["PROFILE", "PARTITION", "QOS", "RUNTIME", "MEM_MB_PER_CPU", "PATH"]
    _print_table(headers, rows)


def _print_table(headers, rows):
    cols = len(headers)
    widths = [len(h) for h in headers]
    for row in rows:
        for i in range(cols):
            widths[i] = max(widths[i], len(str(row[i])))

    def fmt_row(items):
        return "  ".join(str(items[i]).ljust(widths[i]) for i in range(cols))

    print(fmt_row(headers))
    print("  ".join("-" * w for w in widths))
    for r in rows:
        print(fmt_row(r))
