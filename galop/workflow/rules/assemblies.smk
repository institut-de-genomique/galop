import os


rule hifiasm_nanopore:
    input: os.getcwd() + "/Reads/nanopore_{readset}.fastq"
    output: 
        "Assembly/nanopore/Hifiasm/{readset}/hap1.fasta",
        "Assembly/nanopore/Hifiasm/{readset}/hap2.fasta",
        "Assembly/nanopore/Hifiasm/{readset}/haploid.fasta",
    container: f"docker://ghcr.io/cea-lbgb/galop:{config['container_version']}"
    threads: 36
    shell: """
        echo -e "Hifiasm\t$(hifiasm --version)" >> Assembly/software.versions

        cd Assembly/nanopore/Hifiasm/{wildcards.readset}

        hifiasm --ont -o hifiasm -t {threads} {input}

        awk '/^S/{{print ">"$2;print $3}}' hifiasm.bp.p_ctg.gfa > haploid.fasta
        awk '/^S/{{print ">"$2;print $3}}' hifiasm.bp.hap1.p_ctg.gfa > hap1.fasta
        awk '/^S/{{print ">"$2;print $3}}' hifiasm.bp.hap2.p_ctg.gfa > hap2.fasta

        fastoche -f haploid.fasta > haploid.stats
        fastoche -f hap1.fasta > hap1.stats
        fastoche -f hap2.fasta > hap2.stats

        rm hifiasm.bp.* hifiasm.ovlp.* hifiasm.ec.bin
    """


rule hifiasm_pacbio:    
    input: os.getcwd() + "/Reads/pacbio_{readset}.fastq"
    output: 
        "Assembly/pacbio/Hifiasm/{readset}/hap2.fasta",
        "Assembly/pacbio/Hifiasm/{readset}/hap1.fasta",
        "Assembly/pacbio/Hifiasm/{readset}/haploid.fasta",
    container: f"docker://ghcr.io/cea-lbgb/galop:{config['container_version']}"
    threads: 36
    shell: """
        echo -e "Hifiasm\t$(hifiasm --version)" >> Assembly/software.versions
        
        cd Assembly/pacbio/Hifiasm/{wildcards.readset}

        hifiasm -o hifiasm -t {threads} {input}

        awk '/^S/{{print ">"$2;print $3}}' hifiasm.bp.p_ctg.gfa > haploid.fasta
        awk '/^S/{{print ">"$2;print $3}}' hifiasm.bp.hap1.p_ctg.gfa > hap1.fasta
        awk '/^S/{{print ">"$2;print $3}}' hifiasm.bp.hap2.p_ctg.gfa > hap2.fasta

        fastoche -f haploid.fasta > haploid.stats
        fastoche -f hap1.fasta > hap1.stats
        fastoche -f hap2.fasta > hap2.stats

        rm hifiasm.bp.* hifiasm.ovlp.* hifiasm.ec.bin
    """


rule nextdenovo:    
    input: os.getcwd() + "/Reads/{techno}_{readset}.fastq"
    output: "Assembly/{techno}/Nextdenovo/{readset}/{readset}.fasta"
    container: f"docker://ghcr.io/cea-lbgb/galop:{config['container_version']}"
    threads: 36
    params:
        genome_size = config["genome_size"],
        genome_size_bp = config["genome_size"] * 1_000_000
    shell: """
        echo -e "Nextdenovo\t$(nextDenovo --version | tail -n 1 | cut -d ' ' -f 2)" >> Assembly/software.versions

        cd Assembly/{wildcards.techno}/Nextdenovo/{wildcards.readset}

        echo {input} > reads.fofn

        cp /opt/NextDenovo/doc/run_wrapper.cfg run_tmp.cfg
        cat run_tmp.cfg | sed 's/{{threads}}/{threads}/g' | sed 's/{{genomesize}}/{params.genome_size}m/g' > run.cfg
        rm run_tmp.cfg

        nextDenovo run.cfg
        mv rundir/03.ctg_graph/nd.asm.fasta {wildcards.readset}.fasta
        fastoche -f {wildcards.readset}.fasta -m 2000 -g {params.genome_size_bp} > {wildcards.readset}.stats

        rm -r rundir
    """


rule flye:    
    input: os.getcwd() + "/Reads/{techno}_{readset}.fastq"
    output: "Assembly/{techno}/Flye/{readset}.fasta"
    container: f"docker://ghcr.io/cea-lbgb/galop:{config['container_version']}"
    threads: 36
    params:
        genome_size = config["genome_size"],
        genome_size_bp = config["genome_size"] * 1_000_000
    shell: """
        echo -e "Flye\t$(flye --version)" >> Assembly/software.versions

        cd Assembly/{wildcards.techno}/Flye/

        flye --nano-hq {input} -t {threads} -g {params.genome_size}m -o {wildcards.readset}

        cd ..
        mv {wildcards.readset}/assembly.fasta {wildcards.readset}.fasta
        mv {wildcards.readset}/assembly_info.txt {wildcards.readset}.assembly_info.txt

        fastoche -f {wildcards.readset}.fasta -m 2000 -g {params.genome_size_bp} > {wildcards.readset}.stats

        rm -r {wildcards.readset}
    """


rule hifiasm_hybrid:
    input: 
        nanopore = os.getcwd() + "/Reads/nanopore_full.fastq",
        pacbio = os.getcwd() + "/Reads/pacbio_full.fastq"
    output:
        "Assembly/hybrid/Hifiasm/full/hap1.fasta",
        "Assembly/hybrid/Hifiasm/full/hap2.fasta",
        "Assembly/hybrid/Hifiasm/full/haploid.fasta"
    container: f"docker://ghcr.io/cea-lbgb/galop:{config['container_version']}"
    threads: 36
    shell: """
        echo -e "Hifiasm\t$(hifiasm --version)" >> Assembly/software.versions
        
        cd Assembly/hybrid/Hifiasm/full

        hifiasm -o hifiasm -t {threads} --ont {input.nanopore} {input.pacbio}

        awk '/^S/{{print ">"$2;print $3}}' hifiasm.bp.p_ctg.gfa > haploid.fasta
        awk '/^S/{{print ">"$2;print $3}}' hifiasm.bp.hap1.p_ctg.gfa > hap1.fasta
        awk '/^S/{{print ">"$2;print $3}}' hifiasm.bp.hap2.p_ctg.gfa > hap2.fasta

        fastoche -f haploid.fasta > haploid.stats
        fastoche -f hap1.fasta > hap1.stats
        fastoche -f hap2.fasta > hap2.stats

        rm hifiasm.bp.* hifiasm.ec.bin hifiasm.ovlp.*
    """


rule hifiasm_hic:
    input: 
        long_reads = os.getcwd() + "/Reads/{techno}_{readset}.fastq",
        hic_r1 = config["hic_r1"],
        hic_r2 = config["hic_r2"]
    output: 
        "Assembly/{techno}_hic/Hifiasm/{readset}/hap1.fasta",
        "Assembly/{techno}_hic/Hifiasm/{readset}/hap2.fasta",
        "Assembly/{techno}_hic/Hifiasm/{readset}/haploid.fasta",
    container: f"docker://ghcr.io/cea-lbgb/galop:{config['container_version']}"
    threads: 36
    shell: """
        echo -e "Hifiasm\t$(hifiasm --version)" >> Assembly/software.versions

        cd Assembly/{wildcards.techno}_hic/Hifiasm/{wildcards.readset}

        ont_flag=""
        if [[ "{input}" =~ "nanopore" ]]; then
            ont_flag="--ont"
        fi

        hifiasm ${{ont_flag}} -o hifiasm -t {threads} --h1 {input.hic_r1} --h2 {input.hic_r2} {input.long_reads}

        awk '/^S/{{print ">"$2;print $3}}' hifiasm.hic.p_ctg.gfa > haploid.fasta
        awk '/^S/{{print ">"$2;print $3}}' hifiasm.hic.hap1.p_ctg.gfa > hap1.fasta
        awk '/^S/{{print ">"$2;print $3}}' hifiasm.hic.hap2.p_ctg.gfa > hap2.fasta

        fastoche -f haploid.fasta > haploid.stats
        fastoche -f hap1.fasta > hap1.stats
        fastoche -f hap2.fasta > hap2.stats

        rm hifiasm.hic.*
    """

rule hifiasm_hybrid_hic:
    input: 
        nanopore = os.getcwd() + "/Reads/nanopore_full.fastq",
        pacbio = os.getcwd() + "/Reads/pacbio_full.fastq",
        hic_r1 = config["hic_r1"],
        hic_r2 = config["hic_r2"]
    output: 
        "Assembly/hybrid_hic/Hifiasm/{readset}/hap1.fasta",
        "Assembly/hybrid_hic/Hifiasm/{readset}/hap2.fasta",
        "Assembly/hybrid_hic/Hifiasm/{readset}/haploid.fasta"
    container: f"docker://ghcr.io/cea-lbgb/galop:{config['container_version']}"
    threads: 36
    shell: """
        echo -e "Hifiasm\t$(hifiasm --version)" >> Assembly/software.versions

        cd Assembly/hybrid_hic/Hifiasm/{wildcards.readset}

        hifiasm --ont {input.nanopore} -o hifiasm -t {threads} --h1 {input.hic_r1} --h2 {input.hic_r2} {input.pacbio}

        awk '/^S/{{print ">"$2;print $3}}' hifiasm.hic.p_ctg.gfa > haploid.fasta
        awk '/^S/{{print ">"$2;print $3}}' hifiasm.hic.hap1.p_ctg.gfa > hap1.fasta
        awk '/^S/{{print ">"$2;print $3}}' hifiasm.hic.hap2.p_ctg.gfa > hap2.fasta

        fastoche -f haploid.fasta > haploid.stats
        fastoche -f hap1.fasta > hap1.stats
        fastoche -f hap2.fasta > hap2.stats

        rm hifiasm.hic.*
    """
