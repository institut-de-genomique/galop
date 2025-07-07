rule concatenate_nanopore:
    input: config["nanopore_input_file"]
    output: "Reads/nanopore_full.fastq"
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


rule concatenate_pacbio:
    input: config["pacbio_input_file"]
    output: "Reads/pacbio_full.fastq"
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


rule extract_longest:
    input: "Reads/nanopore_full.fastq"
    output: "Reads/nanopore_longest.fastq"
    container: f"docker://ghcr.io/cea-lbgb/galop:{config['container_version']}"
    params:
        genome_size = config["genome_size"],
        readset_coverage = config["readset_coverage"]
    shell: """
        get_longest -f {input} -g {params.genome_size} -c {params.readset_coverage} -o {output}
    """


rule filtlong:
    input: "Reads/nanopore_full.fastq"
    output: "Reads/nanopore_filtlong.fastq"
    container: f"docker://ghcr.io/cea-lbgb/galop:{config['container_version']}"
    params:
        kept_bases = config["genome_size"] * config["readset_coverage"] * 1_000_000
    shell: """
        filtlong -t {params.kept_bases} {input} > {output}
    """