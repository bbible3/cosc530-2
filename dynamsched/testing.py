from config import Config
from log import Log, LogType
from instructiontypes import InstructionTypes, InstructionType, DefaultInstructionTypes


#Are we running this file directly?
if __name__ == "__main__":
    log = Log()
    config = Config(log=log)
    config.print()
    log.print()

    instruction_types = DefaultInstructionTypes.default_instruction_types()
    instruction_types.print()