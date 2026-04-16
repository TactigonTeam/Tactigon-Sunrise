from dataclasses import dataclass

@dataclass
class ComauConfig:
    command_topic: str = "/robot/comau/action"
    response_topic: str = "/robot/comau/action_result"

    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            json.get("command_topic", "/robot/comau/action"),
            json.get("response_topic", "/robot/comau/action_result"),
        )
    
    def toJSON(self) -> dict:
        return dict(
            command_topic=self.command_topic,
            response_topic=self.response_topic
        )