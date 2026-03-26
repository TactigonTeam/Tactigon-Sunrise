import asyncio
import socket
import time

from threading import Thread, Event

class MockRobot(Thread):
    HOST = "0.0.0.0"
    MOTION_SERVER_PORT = 1101
    STATE_SERVER_PORT = 1104
    ROBOT_SERVER_PORT = 1105
    stop_flag: Event

    def __init__(self):
        Thread.__init__(self)
        self.stop_flag = Event()

    def run(self):
        self.stop_flag.clear()
        asyncio.run(self._run())

    def join(self, timeout: float | None = None):
        self.stop_flag.set()
        return Thread.join(self, timeout)

    async def _run(self):
        state_server = await asyncio.start_server(self.state_handler, self.HOST, self.STATE_SERVER_PORT)
        motion_server = await asyncio.start_server(self.motion_handler, self.HOST, self.MOTION_SERVER_PORT)
        robot_server = await asyncio.start_server(self.robot_handler, self.HOST, self.ROBOT_SERVER_PORT)

        async with state_server, motion_server, robot_server:
            await asyncio.gather(
                state_server.serve_forever(),
                motion_server.serve_forever(),
                robot_server.serve_forever(),
            )

    async def state_handler(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        while not self.stop_flag.is_set():
            writer.write(self._build_state_message().encode())

            print("[MOCK ROBOT] Sent READY state")
            time.sleep(1 / 25)  # ~25Hz come robot reale

    async def motion_handler(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        while not self.stop_flag.is_set():
            time.sleep(1 / 25)  # ~25Hz come robot reale

    async def robot_handler(self, rreader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        while not self.stop_flag.is_set():
            time.sleep(1 / 25)  # ~25Hz come robot reale

    def _build_state_message(self):
        timestamp = int(time.time())
        robot_status = "R"   # READY
        sts_selector = 2     # AUTO
        sensor_type = 0

        joints = [0.0] * 10
        ee = [0.0] * 6
        din = [0] * 6
        dout = [0] * 6

        error = 0
        num_joints = 6
        jnt_type = [0] * 10

        # Costruzione messaggio (come WRITE)
        msg = [
            timestamp,
            robot_status,
            sts_selector,
            sensor_type,
            *joints,
            *ee,
            *din,
            *dout,
            error,
            num_joints,
            *jnt_type
        ]

        # STRINGA separata da spazi (IMPORTANTISSIMO)
        return "".join(map(str, msg)) + "\n"


# def fake_robot_server():
#     server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server.bind((HOST, PORT))
#     server.listen(1)

#     print(f"[MOCK ROBOT] Listening on {PORT}...")

#     conn, addr = server.accept()
#     print(f"[MOCK ROBOT] Connected by {addr}")

#     try:
#         while True:
#             msg = build_state_message()
#             conn.sendall(msg.encode())

#             print("[MOCK ROBOT] Sent READY state")
#             time.sleep(1 / 25)  # ~25Hz come robot reale

#     except Exception as e:
#         print(f"[MOCK ROBOT] Error: {e}")

#     finally:
#         conn.close()


if __name__ == "__main__":
    f = MockRobot()
    f.start()
    input("Premi un tasto per spegnere")
    f.join(10)
