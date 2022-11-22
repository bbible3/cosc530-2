from config import Config
from sim import Sim
from log import Log, LogType
from instructiontypes import InstructionTypes, InstructionType, DefaultInstructionTypes
from tracer import Tracer

#Are we running this file directly?
if __name__ == "__main__":
    log = Log()
    config = Config(log=log)
    #config.print()
    #log.print()

    instruction_types = DefaultInstructionTypes.default_instruction_types()
    #instruction_types.print()

    tracer = Tracer("trace.dat", log=log, instruction_types=instruction_types)
    #log.print()

    tracer.process()
    #log.print()

    print("About to simulate")
    sim = Sim(config=config, trace=tracer, instruction_types=instruction_types, log=log)
    
    sim.simulate()
    sim.simulate()
    sim.simulate() 
    log.print()