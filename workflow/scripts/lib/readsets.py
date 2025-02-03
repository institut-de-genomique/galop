from lib.config import ReadsetConfig
import os


def concat_reads(runner, rc: ReadsetConfig):
    project_codes = [elt[0].split(",")[0] for elt in rc.project_codes]
    materials = [elt[0].split(",")[1:] for elt in rc.project_codes]

    cmd = 'echo "" > Reads/used_readsets.txt\n'
    if rc.use_all_readsets and not rc.pacbio:
        for i, project_code in enumerate(project_codes):
            for material in materials[i]:
                cmd += f"\nfind /env/cns/proj/projet_{project_code}/{material}/RunsNanopore/ -name '*.fastq' >> " \
                       f"Reads/used_readsets.txt\n"
                cmd += f"find /env/cns/proj/projet_{project_code}/{material}/RunsNanopore/ -name '*.fastq' | " \
                       f"xargs -I {{}} bash  -c 'cat {{}} >> Reads/full.fastq'\n"
                cmd += f"find /env/cns/proj/projet_{project_code}/{material}/RunsNanopore/ -name '*.fastq.gz' >> " \
                       f"Reads/used_readsets.txt\n"
                cmd += f"find /env/cns/proj/projet_{project_code}/{material}/RunsNanopore/ -name '*.fastq.gz' | " \
                       f"xargs -I {{}} bash  -c 'gunzip -c {{}} >> Reads/full.fastq'\n"
    elif rc.use_all_readsets and rc.pacbio:
        for i, project_code in enumerate(project_codes):
            for material in materials[i]:
                cmd += f"\nfind /env/cns/proj/projet_{project_code}/{material}/RunsPacbio/ -name '*.fastq' >> " \
                       f"Reads/used_readsets.txt\n"
                cmd += f"find /env/cns/proj/projet_{project_code}/{material}/RunsPacbio/ -name '*.fastq' | xargs -I " \
                       f"{{}} bash  -c 'cat {{}} >> Reads/full.fastq'\n"
                cmd += f"find /env/cns/proj/projet_{project_code}/{material}/RunsPacbio/ -name '*.fastq.gz' >> " \
                       f"Reads/used_readsets.txt\n"
                cmd += f"find /env/cns/proj/projet_{project_code}/{material}/RunsPacbio/ -name '*.fastq.gz' | xargs " \
                       f"-I {{}} bash  -c 'gunzip -c {{}} >> Reads/full.fastq'\n"
    elif not rc.use_all_readsets and not rc.pacbio:
        cmd += "module load extenv/rdbioseq commontools \n"
        for i, project_code in enumerate(project_codes):
            for material in materials[i]:
                cmd += f"\nlsRunProj -format path,filename,validProd,validBioinfo,nbnt,techversion,location,nanoporeBasecallerVersion -p " \
                       f"{project_code},{material} -tech nanopore | " \
                       f"awk \'BEGIN{{OFS=\"\\t\"}}{{if($4==1 && $7==\"CNS\"){{print $1\"/\"$2, $5, $6}}}}\' >> " \
                       f"Reads/used_readsets.txt\n"
                cmd += f"lsRunProj -format path,filename,validProd,validBioinfo,location,nanoporeBasecallerVersion -p {project_code},{material}" \
                       f" -tech nanopore | awk '{{if($4==1 && $5==\"CNS\"){{print $1\"/\"$2}}}}' | xargs -I " \
                       f"{{}} bash  -c 'zcat -f {{}} >> Reads/full.fastq'\n"
    else:
        cmd += "module load extenv/rdbioseq commontools \n"
        for i, project_code in enumerate(project_codes):
            for material in materials[i]:
                cmd += f"\nlsRunProj -format path,filename,validProd,validBioinfo,nbnt,techversion,location,nanoporeBasecallerVersion -p " \
                       f"{project_code},{material} -tech pacbio | " \
                       f"awk \'BEGIN{{OFS=\"\\t\"}}{{if($4==1 && $7==\"CNS\"){{print $1\"/\"$2, $5, $6}}}}\' >> " \
                       f"Reads/used_readsets.txt\n"
                cmd += f"lsRunProj -format path,filename,validProd,validBioinfo,location,nanoporeBasecallerVersion -p {project_code},{material}" \
                       f" -tech pacbio | awk '{{if($4==1 && $5==\"CNS\"){{print $1\"/\"$2}}}}' | xargs -I " \
                       f"{{}} bash  -c 'zcat -f {{}} >> Reads/full.fastq'\n"

    concat_job = runner.add_job(
        cmd=cmd, name="readsets_concat_reads", queue=rc.queue, cpus=2, memory=20, qos=rc.qos
    )
    return concat_job


def dedup_read_names(runner, rc: ReadsetConfig, concat_job):
    cmd = "module load extenv/ig c/gnu/7.3.0 c++/gnu/7.3.0\n"
    cmd += f"\n{rc.script_path}/tools/benchme {rc.script_path}/tools/seqkit rmdup -n -j 2 -o Reads/full_filt.fastq " \
           f"Reads/full.fastq\n"
    cmd += "mv Reads/full_filt.fastq Reads/full.fastq"

    if concat_job != 0:
        dedup_job = runner.add_job(
            cmd=cmd,
            name="readsets_dedup_read_names",
            queue=rc.queue,
            cpus=2,
            qos=rc.qos,
            memory=20,
            dependency_list=[concat_job],
            dependency_type="afterok",
        )
    else:
        dedup_job = runner.add_job(
            cmd=cmd,
            name="readsets_dedup_read_names",
            queue=rc.queue,
            cpus=2,
            qos=rc.qos,
            memory=20,
        )
    return dedup_job


def filtlong(runner, rc: ReadsetConfig, dedup_read_names_job):
    cmd = "module load extenv/ig c/gnu/7.3.0 c++/gnu/7.3.0\n"
    cmd += f"{rc.script_path}/tools/benchme {rc.script_path}/tools/filtlong/bin/filtlong -t " \
           f"{int(rc.genome_size) * rc.coverage * 1000000} Reads/full.fastq > Reads/filtlong.fastq"

    filtlong_job = runner.add_job(
        cmd=cmd,
        name="readsets_filtlong",
        queue=rc.queue,
        cpus=2,
        qos=rc.qos,
        memory=20,
        dependency_list=[dedup_read_names_job],
        dependency_type="afterok",
    )
    return filtlong_job


def longest(runner, rc: ReadsetConfig, dedup_read_names_job):
    cmd = "module load extenv/ig c/gnu/7.3.0 c++/gnu/7.3.0\n"
    cmd += f"{rc.script_path}/tools/benchme {rc.script_path}/tools/get_longest_nap/get_longest_nap -f " \
           f"Reads/full.fastq -g {rc.genome_size} -o Reads/longest.fastq -c {rc.coverage}"

    longest_job = runner.add_job(
        cmd=cmd,
        name="readsets_longest",
        queue=rc.queue,
        cpus=2,
        qos=rc.qos,
        memory=20,
        dependency_list=[dedup_read_names_job],
        dependency_type="afterok",
    )
    return longest_job


def launch_readsets_creation(runner, readset_config: ReadsetConfig):
    print("\nReadsets creation")

    readset_list = readset_config.readset_list.split(",")
    for i in range(0, len(readset_list)):
        readset_list[i] = readset_list[i].upper()

    concat_reads_job = 0
    filtlong_job = 0
    longest_job = 0

    # Total readset
    if readset_config.input_file != "":
        os.system(f"ln -s {readset_config.input_file} Reads/full.fastq")
    else:
        concat_reads_job = concat_reads(runner, readset_config)

    dedup_read_names_job = dedup_read_names(runner, readset_config, concat_reads_job)
    launch_fastoche(runner, readset_config, "full", "Reads/full.fastq", dedup_read_names_job)

    # Filtlong readset
    if "FILTLONG" in readset_list:
        filtlong_job = filtlong(runner, readset_config, dedup_read_names_job)
        launch_fastoche(runner, readset_config, "filtlong", "Reads/filtlong.fastq", filtlong_job)

    # Longest readset
    if "LONGEST" in readset_list:
        longest_job = longest(runner, readset_config, dedup_read_names_job)
        launch_fastoche(runner, readset_config, "longest", "Reads/longest.fastq", longest_job)

    runner.run(wait=readset_config.wait)
    return dedup_read_names_job, filtlong_job, longest_job


def launch_fastoche(runner, rc: ReadsetConfig, readset_name, readset, dependency):
    cmd = "module load extenv/ig extenv/rdbioseq fastoche\n"
    cmd += f"fastoche -f {readset} > Reads/{readset_name}.stats"

    runner.add_job(
        cmd=cmd, name=f"fastoche_{readset_name}", queue=rc.queue, cpus=2, memory=20,
        dependency_list=[dependency], dependency_type="afterok",
    )
