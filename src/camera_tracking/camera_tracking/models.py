from dataclasses import dataclass

@dataclass
class CameraTrackingConfig:
    debug: bool = False
    camera_topic: str = "/braccio_command"
    tracking_topic: str = "/camera_tracking/image"
    marker_tpic: str = "/camera_tracking/markers"
    pointing_topic: str = "/camera_tracking/pointing"
    marker_definition: str = "ARUCO_4X4_100"

    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            json.get("debug", False),
            json.get("camera_topic", "/braccio_command"),
            json.get("tracking_topic", "/camera_tracking/image"),
            json.get("marker_topic", "/camera_tracking/markers"),
            json.get("pointing_topic", "/camera_tracking/pointing"),
            json.get("marker_definition", "ARUCO_4X4_100"),
        )
    
    def toJSON(self) -> dict:
        return dict(
            debug=self.debug,
            camera_topic=self.camera_topic,
            tracking_topic=self.tracking_topic,
            marker_topic=self.marker_tpic,
            pointing_topic=self.pointing_topic,
            marker_definition=self.marker_definition,
        )