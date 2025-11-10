from std_msgs.msg import String

from sunrise.mission_controller.models import MissionControllerConfig, Publisher, Subscription, Message
from sunrise.mission_controller.node import MissionControllerNode
from sunrise.mission_controller import MissionController

def on_message(node: MissionControllerNode, msg: Message):

    print(node, msg)

def main():
    cfg = MissionControllerConfig(
        "MissionController",
        [
            Publisher(
                "sunrise/mission_controller/keepalive",
                String,
                10
            )
        ],
        [
            Subscription(
                "sunrise/mission_controller/test",
                String,
                10
            )
        ]
    )

    with MissionController(cfg, on_message) as mc:
        pass
    # mc = MissionController(cfg, on_message)
    # mc.start()


if __name__ == "__main__":
    main()