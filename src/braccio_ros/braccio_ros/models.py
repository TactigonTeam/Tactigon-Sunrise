from dataclasses import dataclass
from tactigon_arduino_braccio import BraccioConfig as BraccioConfigBase

@dataclass
class BraccioConfig(BraccioConfigBase):
    command_topic: str = "/braccio_command"
    response_topic: str = "/braccio_move_result"

    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            json.get("address", ""),
            json.get("command_topic", "/braccio_command"),
            json.get("response_topic", "/braccio_move_result"),
        )
    
    def toJSON(self) -> dict:
        return dict(
            address=self.address,
            command_topic=self.command_topic,
            response_topic=self.response_topic
        )