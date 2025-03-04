rule concatenate_nanopore:
    input: config["nanopore_input_file"]
    output: "Reads/nanopore.fastq"
    shell: """
        for file in {input}
        do
            if [[ $file == *.gz ]]
            then
                zcat $file >> {output}
            else
                cat $file >> {output}
            fi
        done
    """


rule concatenate_pacbio:
    input: config["pacbio_input_file"]
    output: "Reads/pacbio.fastq"
    shell: """
        for file in {input}
        do
            if [[ $file == *.gz ]]
            then
                zcat $file >> {output}
            else
                cat $file >> {output}
            fi
        done
    """

rule extract_longest:
    input: "Reads/nanopore.fastq"
    output: "Reads/nanopore_longest.fastq"
    container: "docker://ghcr.io/cea-lbgb/galop:0.1"
    params:
        genome_size = config["genome_size"],
        readset_coverage = config["readset_coverage"]
    shell: """
        get_longest -f {input} -g {params.genome_size} -c {params.readset_coverage} -o {output}
    """