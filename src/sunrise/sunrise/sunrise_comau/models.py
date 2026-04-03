from dataclasses import dataclass

@dataclass
class ComauConfig:
    command_topic: str = "/comau_joint_action"
    response_topic: str = "/comau_joint_action_result"

    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            json.get("command_topic", "/comau_joint_action"),
            json.get("response_topic", "/comau_joint_action_result"),
        )
    
    def toJSON(self) -> dict:
        return dict(
            command_topic=self.command_topic,
            response_topic=self.response_topic
        )