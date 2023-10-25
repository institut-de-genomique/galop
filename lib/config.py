class ReadsetConfig():
    def __init__(
            self, script_path, queue, project_codes, genome_size, qos,
            readset_list, coverage, use_all_readsets, input_file="",
            wait=False, pacbio=False,
    ):
        self.script_path = script_path
        self.queue = queue
        self.project_codes = project_codes
        self.genome_size = genome_size
        self.qos = qos
        self.readset_list = readset_list
        self.coverage = coverage
        self.use_all_readsets = use_all_readsets
        self.input_file = input_file
        self.wait = wait
        self.pacbio = pacbio


class Config:
    def __init__(self, genome_size, hq_reads, script_path, queue, nb_cores, qos, time_limit):
        self.genome_size = genome_size
        self.hq_reads = hq_reads
        self.script_path = script_path
        self.queue = queue
        self.nb_cores = nb_cores
        self.qos = qos
        self.time_limit = time_limit