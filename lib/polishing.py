import os


def launch_racon(
    runner,
    script_path,
    assembly_dir,
    queue,
    core_number,
    qos,
    assembly,
    time_limit,
):
    # racon_job = job.Job("racon.sh", queue, core_number, qos, "")

    cmd = "cd Polishing/Racon\n"
    cmd += "module load nanoporetech racon extenv/rdbioseq fastoche\n"
    cmd += "echo -e \"Racon\t$(racon --version)\" > ../software.versions\n"
    cmd += (
        "%s/tools/benchme minimap2 -x map-ont -t %s %s %s/Reads/full.fastq > minimap.paf\n"
        % (script_path, core_number, assembly, assembly_dir)
    )
    cmd += (
        "%s/tools/benchme racon -u -t %s %s/Reads/full.fastq minimap.paf %s > racon.fasta\n"
        % (script_path, core_number, assembly_dir, assembly)
    )
    cmd += "fastoche -f racon.fasta -m 2000 > racon.stats\n"

    racon_job = runner.add_job(
        cmd=cmd,
        name="racon",
        queue=queue,
        cpus=core_number,
        qos=qos,
        memory=core_number * 10 if queue == "normal" else core_number * 30,
        time_limit=time_limit,
    )
    return racon_job


def launch_medaka(
    runner,
    script_path,
    assembly_dir,
    queue,
    core_number,
    qos,
    dependencies,
    assembly,
    model,
    time_limit,
):
    # medaka_job = job.Job("medaka.sh", queue, core_number, qos, dependencies)

    cmd = "cd Polishing\n"
    cmd += "echo -e \"Medaka\t$(apptainer exec /env/cns/bigtmp2/ONT/container/singularity_files/medaka/medaka.img medaka --version | cut -d ' ' -f 2)\" >> software.versions\n"
    cmd += "%s/tools/benchme " % (script_path)
    cmd += "apptainer exec --bind /env:/env \\\n"
    cmd += "  --pwd $(pwd) --containall --no-home /env/cns/bigtmp2/ONT/container/singularity_files/medaka/medaka.img \\\n"
    cmd += (
        "    medaka_consensus -i %s/Reads/full.fastq -d %s -t %s -m %s -o Medaka\n"
        % (assembly_dir, assembly, core_number, model)
    )
    cmd += "module load extenv/rdbioseq fastoche\n"
    cmd += "fastoche -f Medaka/consensus.fasta -m 2000 > Medaka/consensus.stats\n"

    medaka_job = runner.add_job(
        cmd=cmd,
        name="medaka",
        queue=queue,
        cpus=core_number,
        qos=qos,
        memory=core_number * 10 if queue == "normal" else core_number * 30,
        time_limit=time_limit,
        dependency_list=[dependencies] if dependencies != "" else [],
        dependency_type="afterok" if dependencies != "" else None,
    )
    return medaka_job


def launch_hapog(
    runner,
    script_path,
    output_directory,
    queue,
    core_number,
    qos,
    dependencies,
    assembly,
    pe1,
    pe2,
    time_limit,
):
    for i in range(1, 3, 1):
        if i == 2:
            assembly = (
                output_directory + "/Polishing/Hapog/hapog_1/hapog_results/hapog.fasta"
            )

        # hapog_job = job.Job("hapog_%s.sh" % (i), queue, core_number, qos, dependencies)

        cmd = "cd Polishing/Hapog\n"
        # cmd += "module load c/gnu/7.3.0 c++/gnu/7.3.0 biopython minimap2 bwa samtools/1.15.1\n"
        cmd += "module load extenv/rdbioseq hapog fastoche\n"
        cmd += "echo -e \"Hapog\t$(module list -l | grep hapog | cut -d ' ' -f 1)\" >> ../software.versions\n"

        cmd += "python %s/tools/HAPO-G/hapog.py --genome %s -t %s -o hapog_%s" % (
            script_path,
            assembly,
            core_number,
            i,
        )

        for pe in pe1:
            cmd += " --pe1 %s" % (pe)
        for pe in pe2:
            cmd += " --pe2 %s" % (pe)

        cmd += f"\nfastoche -f hapog_{i}/hapog_results/hapog.fasta -m 2000 > hapog_{i}/hapog_results/hapog.stats\n"

        # hapog_job.create_submission_script(main_job, cmd)
        dependencies = runner.add_job(
            cmd=cmd,
            name="hapog_%s" % (i),
            queue=queue,
            cpus=core_number,
            qos=qos,
            memory=core_number * 10 if queue == "normal" else core_number * 30,
            time_limit=time_limit,
            dependency_list=[dependencies] if dependencies != "" else [],
            dependency_type="afterok" if dependencies != "" else None,
        )


def launch_polishing(
    runner,
    script_path,
    output_directory,
    assembly_dir,
    queue,
    nb_cores,
    qos,
    with_racon,
    no_medaka,
    assembly,
    time_limit,
    medaka_model="",
    pe1="",
    pe2="",
    wait=False,
):
    dependencies = ""
    if with_racon:
        dependencies = launch_racon(
            runner, script_path, assembly_dir, queue, nb_cores, qos, assembly, time_limit
        )
        assembly = os.path.join(output_directory, "Polishing", "Racon", "racon.fasta")

    if not no_medaka:
        dependencies = launch_medaka(
            runner,
            script_path,
            assembly_dir,
            queue,
            nb_cores,
            qos,
            dependencies,
            assembly,
            medaka_model,
            time_limit,
        )
        assembly = os.path.join(
            output_directory, "Polishing", "Medaka", "consensus.fasta"
        )

    if pe1 and pe2:
        launch_hapog(
            runner,
            script_path,
            output_directory,
            queue,
            nb_cores,
            qos,
            dependencies,
            assembly,
            pe1,
            pe2,
            time_limit,
        )

    runner.run(wait=wait)
