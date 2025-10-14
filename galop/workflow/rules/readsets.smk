import os


rule concatenate_nanopore:
    input: config["nanopore_input_file"]
    output: os.getcwd() + "/Reads/nanopore_full.fastq"
    run:
        import os

        shell("mkdir -p Reads")

        for i in input:
            if i.endswith(".gz"):
                shell(f"zcat {i} >> {output}")
            else:
                shell(f"cat {i} >> {output}")


rule nanopore_full_stats:
    input: rules.concatenate_nanopore.output
    output: "Reads/nanopore_full.stats"
    container: f"docker://ghcr.io/cea-lbgb/galop:{config['container_version']}"
    shell: """
        fastoche -f {input} > {output}
    """


rule concatenate_pacbio:
    input: config["pacbio_input_file"]
    output: os.getcwd() + "/Reads/pacbio_full.fastq"
    run:
        import os

        if len(input) == 1 and not input[0].endswith(".gz"):
            shell(f"ln -s {abspath} {output}")

        else:
            for i in input:
                if i.endswith(".gz"):
                    shell(f"zcat {i} >> {output}")
                else:
                    shell(f"cat {i} >> {output}")


rule pacbio_full_stats:
    input: rules.concatenate_pacbio.output
    output: "Reads/pacbio_full.stats"
    container: f"docker://ghcr.io/cea-lbgb/galop:{config['container_version']}"
    shell: """
        fastoche -f {input} > {output}
    """


rule extract_longest:
    input: os.getcwd() + "/Reads/nanopore_full.fastq"
    output: os.getcwd() + "/Reads/nanopore_longest.fastq"
    container: f"docker://ghcr.io/cea-lbgb/galop:{config['container_version']}"
    params:
        genome_size = config["genome_size"],
        readset_coverage = config["readset_coverage"]
    shell: """
        get_longest -f {input} -g {params.genome_size} -c {params.readset_coverage} -o {output}
    """


rule nanopore_longest_stats:
    input: rules.extract_longest.output
    output: "Reads/nanopore_longest.stats"
    container: f"docker://ghcr.io/cea-lbgb/galop:{config['container_version']}"
    shell: """
        fastoche -f {input} > {output}
    """


rule filtlong:
    input: os.getcwd() + "/Reads/nanopore_full.fastq"
    output: os.getcwd() + "/Reads/nanopore_filtlong.fastq"
    container: f"docker://ghcr.io/cea-lbgb/galop:{config['container_version']}"
    params:
        kept_bases = config["genome_size"] * config["readset_coverage"] * 1_000_000
    shell: """
        filtlong -t {params.kept_bases} {input} > {output}
    """


rule nanopore_filtlong_stats:
    input: rules.filtlong.output
    output: "Reads/nanopore_filtlong.stats"
    container: f"docker://ghcr.io/cea-lbgb/galop:{config['container_version']}"
    shell: """
        fastoche -f {input} > {output}
    """
