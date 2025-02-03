def launch_flye(
    runner,
    script_path,
    genome_size,
    readset_name,
    readset,
    queue,
    nb_cores,
    qos,
    readset_job,
    hq_reads,
    time_limit,
):
    mode = "--nano-raw"
    if hq_reads:
        mode = "--nano-hq"

    cmd = "cd Assembly/Flye/\n"
    cmd += "module unload python/* python2/* python3/*\n"
    cmd += "module load extenv/ig extenv/rdbioseq fastoche c/gnu/7.3.0 c++/gnu/7.3.0 python/3.7\n"
    cmd += "echo -e \"Flye\t$(%s/tools/flye/bin/flye --version)\" >> ../software.versions\n"
    cmd += "%s/tools/benchme %s/tools/flye/bin/flye %s %s -t %s -g %sm -o %s\n" % (
        script_path,
        script_path,
        mode,
        readset,
        nb_cores,
        int(genome_size),
        readset_name,
    )

    cmd += "mv %s/assembly.fasta %s.fasta\n" % (readset_name, readset_name)
    cmd += "mv %s/assembly_info.txt %s.assembly_info.txt\n" % (
        readset_name,
        readset_name,
    )

    cmd += "fastoche -f %s.fasta -m 2000 -g %s > %s.stats\n" % (
        readset_name,
        int(genome_size * 1000000),
        readset_name,
    )

    flye_job = runner.add_job(
        cmd=cmd,
        name="flye_%s" % (readset_name),
        queue=queue,
        cpus=nb_cores,
        qos=qos,
        memory=nb_cores * 10 if queue == "normal" else nb_cores * 30,
        time_limit=time_limit,
        dependency_list=readset_job,
        dependency_type="afterok",
    )
    return flye_job


def launch_necat(
    runner,
    script_path,
    genome_size,
    readset_name,
    readset,
    queue,
    nb_cores,
    qos,
    readset_job,
    hq_reads,
    time_limit,
):
    cmd = "reads=%s\n" % (readset)
    cmd += "cd Assembly/\n"
    cmd += "module load extenv/ig extenv/rdbioseq fastoche perl_rdbioseq c/gnu/7.3.0 c++/gnu/7.3.0\n"
    cmd += "export PATH=%s/tools/NECAT/Linux-amd64/bin:$PATH\n" % (script_path)
    cmd += "echo -e \"Necat\t$(head -n 1 %s/tools/NECAT/Linux-amd64/VERSION | cut -d ' ' -f 2)\" >> software.versions\n"
    cmd += "\nnecat.pl config config.txt\n"
    cmd += (
        "cat config.txt | sed 's/PROJECT=.*$/PROJECT=Necat/g' | sed 's/ONT_READ_LIST=.*$/ONT_READ_LIST=reads.txt/g' | sed 's/GENOME_SIZE=.*$/GENOME_SIZE=%s000000/g' | sed 's/THREADS=4.*$/THREADS=%s/g' > config_tmp.txt\n"
        % (int(genome_size), nb_cores)
    )
    cmd += "mv config_tmp.txt config.txt\n"
    cmd += "echo $reads > reads.txt\n"
    cmd += "\n%s/tools/benchme necat.pl bridge config.txt\n" % (script_path)

    cmd += "mv Necat/6-bridge_contigs/polished_contigs.fasta Necat/\n"
    cmd += "mv Necat/6-bridge_contigs/bridged_contigs.fasta Necat/\n"

    cmd += (
        "\nfastoche -f Necat/polished_contigs.fasta -m 2000 -g %s > Necat/polished_contigs.stats\n"
        % (int(genome_size * 1000000))
    )

    necat_job = runner.add_job(
        cmd=cmd,
        name="necat_%s" % (readset_name),
        queue=queue,
        cpus=nb_cores,
        qos=qos,
        memory=nb_cores * 10 if queue == "normal" else nb_cores * 30,
        time_limit=time_limit,
        dependency_list=readset_job,
        dependency_type="afterok",
    )
    return necat_job


def launch_raven(
    runner,
    script_path,
    genome_size,
    readset_name,
    readset,
    queue,
    nb_cores,
    qos,
    readset_job,
    hq_reads,
    time_limit,
):
    cmd = "cd Assembly/Raven/\n"
    cmd += "mkdir %s && cd %s\n" % (readset_name, readset_name)
    cmd += "module load extenv/ig extenv/rdbioseq fastoche c/gnu/7.3.0 c++/gnu/7.3.0 zlib/original/1.2.8 python/3.7\n"
    cmd += (
        "%s/tools/benchme %s/tools/raven/build/bin/raven -t %s -p 1 %s > %s_consensus.fasta\n"
        % (
            script_path,
            script_path,
            nb_cores,
            readset,
            readset_name,
        )
    )
    cmd += "mv %s_consensus.fasta ../%s.fasta\n" % (readset_name, readset_name)
    cmd += "fastoche -f ../%s.fasta -m 2000 -g %s > ../%s_consensus.stats" % (
        readset_name,
        int(genome_size * 1000000),
        readset_name,
    )

    raven_job = runner.add_job(
        cmd=cmd,
        name="raven_%s" % (readset_name),
        queue=queue,
        cpus=nb_cores,
        qos=qos,
        memory=nb_cores * 10 if queue == "normal" else nb_cores * 30,
        time_limit=time_limit,
        dependency_list=readset_job,
        dependency_type="afterok",
    )
    return raven_job


def launch_smartdenovo(
    runner,
    script_path,
    genome_size,
    readset_name,
    readset,
    queue,
    nb_cores,
    qos,
    readset_job,
    hq_reads,
    time_limit,
):
    cmd = "cd Assembly/Smartdenovo/\n"
    cmd += "module load extenv/ig extenv/rdbioseq fastoche c/gnu/7.3.0 c++/gnu/7.3.0 python/3.7\n"
    cmd += "echo -e \"Smartdenovo\t8488de9\" >> ../software.versions\n"
    cmd += (
        "%s/tools/smartdenovo/smartdenovo.pl -p %s -t %s -k 17 -c 1 %s > %s.make\n"
        % (
            script_path,
            readset_name,
            nb_cores,
            readset,
            readset_name,
        )
    )
    cmd += "%s/tools/benchme make -f %s.make\n" % (script_path, readset_name)
    cmd += "find . -name '%s*' -not -name '*.dmo.cns' -not -name '*.make' -delete\n" % (
        readset_name
    )
    cmd += "fastoche -f %s.dmo.cns -m 2000 -g %s > %s.stats\n" % (
        readset_name,
        int(genome_size * 1000000),
        readset_name,
    )
    cmd += "mv %s.dmo.cns %s.fasta" % (readset_name, readset_name)

    smartdenovo_job = runner.add_job(
        cmd=cmd,
        name="smartdenovo_%s" % (readset_name),
        queue=queue,
        cpus=nb_cores,
        qos=qos,
        memory=nb_cores * 10 if queue == "normal" else nb_cores * 30,
        time_limit=time_limit,
        dependency_list=readset_job,
        dependency_type="afterok",
    )
    return smartdenovo_job


def launch_wtdbg2(
    runner,
    script_path,
    genome_size,
    readset_name,
    readset,
    queue,
    nb_cores,
    qos,
    readset_job,
    hq_reads,
    time_limit,
):
    cmd = "cd Assembly/Wtdbg2/\n"
    cmd += "module load extenv/ig extenv/rdbioseq fastoche c/gnu/7.3.0 c++/gnu/7.3.0 python/3.7\n"
    cmd += "echo -e \"Wtdbg2\t$(%s/tools/wtdbg2/wtdbg2 --version | cut -d ' ' -f 2)\" >> ../software.versions\n"
    cmd += (
        "%s/tools/benchme %s/tools/wtdbg2/wtdbg2 -i %s -xont -X5000 -g%sm -o wtdbg2_%s -t %s\n"
        % (
            script_path,
            script_path,
            readset,
            int(genome_size),
            readset_name,
            nb_cores,
        )
    )
    cmd += (
        "%s/tools/benchme %s/tools/wtdbg2/wtpoa-cns -i wtdbg2_%s.ctg.lay.gz -t %s -fo wtdbg2_%s.ctg.lay.fasta\n"
        % (script_path, script_path, readset_name, nb_cores, readset_name)
    )
    cmd += (
        "fastoche -f wtdbg2_%s.ctg.lay.fasta -m 2000 -g %s > wtdbg2_%s.ctg.lay.stats\n"
        % (readset_name, int(genome_size * 1000000), readset_name)
    )
    cmd += "find . -name 'wtdbg2_%s*' -not -name 'wtdbg2_%s.ctg.lay.*' -delete" % (
        readset_name,
        readset_name,
    )

    wtdbg2_job = runner.add_job(
        cmd=cmd,
        name="wtdbg2_%s" % (readset_name),
        queue=queue,
        cpus=nb_cores,
        qos=qos,
        memory=nb_cores * 10 if queue == "normal" else nb_cores * 30,
        time_limit=time_limit,
        dependency_list=readset_job,
        dependency_type="afterok",
    )
    return wtdbg2_job


def launch_hifiasm(
    runner,
    script_path,
    genome_size,
    readset_name,
    readset,
    queue,
    nb_cores,
    qos,
    readset_job,
    hq_reads,
    time_limit,
):
    cmd = "cd Assembly/Hifiasm/\n"
    cmd += "module load extenv/ig extenv/rdbioseq fastoche hifiasm_rdbioseq\n"
    cmd += "echo -e \"Hifiasm\t$(hifiasm --version)\" >> ../software.versions\n"

    cmd += "mkdir %s && cd %s\n" % (readset_name, readset_name)
    cmd += "%s/tools/benchme hifiasm -o hifiasm -t %s %s\n" % (
        script_path,
        nb_cores,
        readset,
    )
    cmd += "awk '/^S/{print \">\"$2;print $3}' hifiasm.bp.p_ctg.gfa > haploid.fasta\n"
    cmd += "awk '/^S/{print \">\"$2;print $3}' hifiasm.bp.hap1.p_ctg.gfa > hap1.fasta\n"
    cmd += (
        "awk '/^S/{print \">\"$2;print $3}' hifiasm.bp.hap2.p_ctg.gfa > hap2.fasta\n\n"
    )

    cmd += "fastoche -f haploid.fasta -m 2000 -g %s > haploid.stats\n" % (
        int(genome_size * 1000000)
    )
    cmd += "fastoche -f hap1.fasta -m 2000 -g %s > hap1.stats\n" % (
        int(genome_size * 1000000)
    )
    cmd += "fastoche -f hap2.fasta -m 2000 -g %s > hap2.stats\n" % (
        int(genome_size * 1000000)
    )

    hifiasm_job = runner.add_job(
        cmd=cmd,
        name="hifiasm_%s" % (readset_name),
        queue=queue,
        cpus=nb_cores,
        qos=qos,
        memory=nb_cores * 10 if queue == "normal" else nb_cores * 30,
        time_limit=time_limit,
        dependency_list=readset_job,
        dependency_type="afterok",
    )
    return hifiasm_job


def launch_nextdenovo(
    runner,
    script_path,
    genome_size,
    readset_name,
    readset,
    queue,
    nb_cores,
    qos,
    readset_job,
    hq_reads,
    time_limit,
):
    cmd = f"mkdir -p Assembly/Nextdenovo/{readset_name}\n"
    cmd += f"cd Assembly/Nextdenovo/{readset_name}\n\n"

    cmd += "module load extenv/rdbioseq fastoche nextdenovo_rdbioseq\n\n"
    cmd += "echo -e \"Nextdenovo\t$(nextDenovo --version | tail -n 1 | cut -d ' ' -f 2)\" >> ../software.versions\n"
    cmd += f"echo '{readset}' > reads.fofn\n"
    cmd += "cp /env/ig/soft/rdbioseq/nextdenovo_rdbioseq/2.5.1/doc/run_wrapper.cfg run_tmp.cfg\n"
    cmd += f"cat run_tmp.cfg | sed 's/{{threads}}/{nb_cores}/g' | sed 's/{{genomesize}}/{genome_size}m/g' > run.cfg\n"
    cmd += "rm run_tmp.cfg\n\n"

    cmd += f"\n{script_path}/tools/benchme nextDenovo run.cfg\n"
    cmd += f"mv rundir/03.ctg_graph/nd.asm.fasta {readset_name}.fasta\n"
    cmd += f"fastoche -f {readset_name}.fasta -m 2000 -g {int(genome_size * 1000000)} > {readset_name}.stats\n\n"

    cmd += "rm -r rundir"

    nextdenovo_job = runner.add_job(
        cmd=cmd,
        name="nextdenovo_%s" % (readset_name),
        queue=queue,
        cpus=nb_cores,
        qos=qos,
        memory=nb_cores * 10 if queue == "normal" else nb_cores * 30,
        time_limit=time_limit,
        dependency_list=readset_job,
        dependency_type="afterok",
    )
    return nextdenovo_job


def launch_shasta(
        runner,
        script_path,
        genome_size,
        readset_name,
        readset,
        queue,
        nb_cores,
        qos,
        readset_job,
        hq_reads,
        time_limit,
):
    cmd = "mkdir Assembly/Shasta\ncd Assembly/Shasta\n"

    cmd += "module load extenv/rdbioseq fastoche shasta_rdbioseq\n\n"
    cmd += f"shasta --input {readset} --assemblyDirectory {readset_name} --command assemble --threads {nb_cores} --config Nanopore-Phased-Jan2022\n"
    #cmd += f"fastoche -f {readset_name}.fasta -m 2000 -g {int(genome_size * 1000000)} > {readset_name}.stats\n\n"

    shasta_job = runner.add_job(
        cmd=cmd,
        name="shasta_%s" % (readset_name),
        queue=queue,
        cpus=nb_cores,
        qos=qos,
        memory=nb_cores * 10 if queue == "normal" else nb_cores * 30,
        time_limit=time_limit,
        dependency_list=readset_job,
        dependency_type="afterok",
    )
    return shasta_job


def launch_assembly(
    runner,
    script_path,
    output_directory,
    queue,
    nb_cores,
    qos,
    dependency,
    genome_size,
    assembler_list,
    readset_list,
    hq_reads,
    time_limit,
    wait=False,
):
    print("\nAssemblies")

    dict_assembly_function = {
        "FLYE": launch_flye,
        "NECAT": launch_necat,
        "RAVEN": launch_raven,
        "SMARTDENOVO": launch_smartdenovo,
        "WTDBG2": launch_wtdbg2,
        "HIFIASM": launch_hifiasm,
        "NEXTDENOVO": launch_nextdenovo,
        "SHASTA": launch_shasta
    }

    assembler_list = assembler_list.split(",")
    for i in range(0, len(assembler_list)):
        assembler_list[i] = assembler_list[i].upper()

    readset_list = readset_list.split(",")
    for i in range(0, len(readset_list)):
        readset_list[i] = readset_list[i].upper()

    nanopore_job, filtlong_job, longest_job = (
        dependency[0],
        dependency[1],
        dependency[2],
    )
    nanopore_job = None if nanopore_job is None else [nanopore_job]
    filtlong_job = None if filtlong_job is None else [filtlong_job]
    longest_job = None if longest_job is None else [longest_job]

    if "FULL" in readset_list:
        for assembler in assembler_list:
            dict_assembly_function[assembler](
                runner,
                script_path,
                genome_size,
                "full",
                output_directory + "/Reads/full.fastq",
                queue,
                nb_cores,
                qos,
                nanopore_job,
                hq_reads,
                time_limit,
            )

    assembler_list = [
        assembler for assembler in assembler_list if assembler not in ["NECAT", "NEXTDENOVO"]
    ]

    if "FILTLONG" in readset_list:
        for assembler in assembler_list:
            dict_assembly_function[assembler](
                runner,
                script_path,
                genome_size,
                "filtlong",
                output_directory + "/Reads/filtlong.fastq",
                queue,
                nb_cores,
                qos,
                filtlong_job,
                hq_reads,
                time_limit,
            )

    if "LONGEST" in readset_list:
        for assembler in assembler_list:
            dict_assembly_function[assembler](
                runner,
                script_path,
                genome_size,
                "longest",
                output_directory + "/Reads/longest.fastq",
                queue,
                nb_cores,
                qos,
                longest_job,
                hq_reads,
                time_limit,
            )

    runner.run(wait=wait)
