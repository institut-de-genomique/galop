import os
import subprocess


class MainJob:
    def __init__(self, script_path, account, submit_mode, no_launch):
        self.script_path = script_path
        self.account = account
        self.submit_mode = submit_mode
        self.no_launch = no_launch

        self.output_dir = ""
        self.benchme = script_path + "/tools/benchme"


class Job:
    def __init__(self, msub_script_name, queue, nb_cores, qos, dependencies):
        self.msub_script_path = "Submission_scripts/" + msub_script_name
        self.queue = queue
        self.nb_cores = int(nb_cores)
        self.qos = qos
        self.dependencies = dependencies

        self.output = self.msub_script_path.replace(".sh", ".o")
        self.error = self.msub_script_path.replace(".sh", ".e")

    def create_submission_script(self, main_job, command):
        print("-- %s/%s" % (main_job.output_directory, self.msub_script_path))
        with open(self.msub_script_path, "w") as out:
            out.write("#!/bin/bash\n")
            out.write("#MSUB -A %s\n" % (main_job.account))
            out.write("#MSUB -q %s\n" % (self.queue))
            out.write("#MSUB -c %s\n" % (self.nb_cores))

            memory_multiplicator = 10
            if "xlarge" in self.queue:
                memory_multiplicator = 50
            out.write("#MSUB -E '--mem=%sG'\n" % (self.nb_cores * memory_multiplicator))

            if self.dependencies != "":
                out.write("#MSUB -E --dependency=afterok:%s\n" % (self.dependencies))

            time_limit = str(24 * 60 * 60)
            if "xlarge" in self.queue or xxlarge in self.queue:
                time_limit = str(7 * 24 * 60 * 60)

            if self.qos != "":
                out.write("#MSUB -E --qos=%s\n" % (self.qos))
                time_limit = 0
                if self.qos == "long":
                    time_limit = str(3 * 24 * 60 * 60)
                elif self.qos == "week":
                    time_limit = str(7 * 24 * 60 * 60)
                elif self.qos == "nolimit":
                    time_limit = str(100 * 24 * 60 * 60)
            out.write("#MSUB -T %s\n" % (time_limit))

            out.write("#MSUB -o %s\n" % (self.output))
            out.write("#MSUB -e %s\n" % (self.error))
            out.write("\n%s" % (command))

    def submit_script(self, main_job):
        sub_out = ""
        if main_job.submit_mode == "msub" and main_job.no_launch == False:
            sub_out = subprocess.check_output(["ccc_msub", self.msub_script_path])
        elif main_job.submit_mode == "local" and main_job.no_launch == False:
            sub_out = subprocess.run(
                ["bash", self.msub_script_path],
                stdout=open(self.msub_script_path.replace(".sh", ".o"), "w"),
                stderr=open(self.msub_script_path.replace(".sh", ".e"), "w"),
            )
            return "0"

        job_id = "0"
        if main_job.no_launch == False:
            job_id = sub_out.split()[3].strip().decode("utf-8")
            print("Successfully submitted script with jobid %s" % (job_id))

        return job_id
