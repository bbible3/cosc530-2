from operator import contains
from log import Log, LogType

class Config:
    def __init__(self, config_file="config.txt", log=None):
        self.config_file = config_file
        self.config_plaintext = ""

        self.buffers_eff_addr = None
        self.buffers_fp_adds = None
        self.buffers_fp_muls = None
        self.buffers_ints = None
        self.buffers_reorder = None

        self.latencies_fp_add = None
        self.latencies_fp_sub = None
        self.latencies_fp_mul = None
        self.latencies_fp_div = None

        self.log = log

        #Read config file from the txt file
        with open(self.config_file, "r") as f:
            self.config_plaintext = f.read()

        self.process_plaintext()
        

    def process_plaintext(self):
        if self.config_plaintext == "":
            raise Exception("Config file is empty")
        try:
            #Read config file from the txt file line by line
            split_lines = self.config_plaintext.splitlines()
            seeking = None
            for i in range(len(split_lines)):
                this_line = split_lines[i]
                if this_line == "buffers":
                    seeking = "buffers"
                elif this_line == "latencies":
                    seeking = "latencies"
                elif len(this_line) < 1:
                    continue
                else:
                    if seeking is not None:
                        if seeking == "buffers":
                            if this_line.startswith("eff addr"):
                                self.buffers_eff_addr = int(this_line.split(": ")[1])
                            elif this_line.startswith("fp adds"):
                                self.buffers_fp_adds = int(this_line.split(": ")[1])
                            elif this_line.startswith("fp muls"):
                                self.buffers_fp_muls = int(this_line.split(": ")[1])
                            elif this_line.startswith("ints"):
                                self.buffers_ints = int(this_line.split(": ")[1])
                            elif this_line.startswith("reorder"):
                                self.buffers_reorder = int(this_line.split(": ")[1])
                        elif seeking == "latencies":
                            if this_line.startswith("fp_add"):
                                self.latencies_fp_add = int(this_line.split(": ")[1])
                            elif this_line.startswith("fp_sub"):
                                self.latencies_fp_sub = int(this_line.split(": ")[1])
                            elif this_line.startswith("fp_mul"):
                                self.latencies_fp_mul = int(this_line.split(": ")[1])
                            elif this_line.startswith("fp_div"):
                                self.latencies_fp_div = int(this_line.split(": ")[1])
        except Exception as e:
            raise Exception(f"Error in config file: [{e}]")
        if self.log is not None:
            self.log.add(LogType.CONFIG_READ, "Config file read successfully")

    def print(self):
        print(f"Config file: {self.config_file}")
        print("buffers")
        print(f"eff_addr {self.buffers_eff_addr}")
        print(f"fp_adds {self.buffers_fp_adds}")
        print(f"fp_muls {self.buffers_fp_muls}")
        print(f"ints {self.buffers_ints}")
        print(f"reorder {self.buffers_reorder}")
        print("latencies")
        print(f"fp_add {self.latencies_fp_add}")
        print(f"fp_sub {self.latencies_fp_sub}")
        print(f"fp_mul {self.latencies_fp_mul}")
        print(f"fp_div {self.latencies_fp_div}")


if __name__ == "__main__":
    #Running in command line, so we're testing the config file
    log = Log()
    config = Config(log=log)
    config.process_plaintext()
    log.print()
