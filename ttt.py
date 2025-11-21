import json
from src.sunrise.sunrise.mission_controller.leo.models import LEOConfig

with open("config/mission_controller_student.json") as cf:
    c = LEOConfig.FromJSON(json.load(cf))

print(c)