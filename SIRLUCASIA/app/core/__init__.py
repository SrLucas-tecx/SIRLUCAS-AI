from SIRLUCASIA.app.core.intent_manager import IntentManager
from SIRLUCASIA.app.core.memory_manager import MemoryManager
from SIRLUCASIA.app.core.command_manager import CommandManager
    
def __init__(self):

    self.name = "SIRLUCAS AI"
    self.version = "0.1"

    self.intent_manager = IntentManager()
    self.memory_manager = MemoryManager()
    self.command_manager = CommandManager()
    self.command_manager = CommandManager(
        self.memory_manager)
        