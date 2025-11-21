#********************************************************************************
# Copyright (c) 2025 Next Industries s.r.l.
#
# This program and the accompanying materials are made available under the
# terms of the Apache 2.0 which is available at http://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
#
# Contributors:
# Massimiliano Bellino
# Stefano Barbareschi
#********************************************************************************

from dataclasses import dataclass

from sunrise.mission_controller.models.skill import Task, Skill, SkillScope

@dataclass
class TEOConfig:
    tasks: list[Task]
    # skills: list[Skill]

    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            tasks=[Task.FromJSON(skill) for skill in json.get("tasks", [])]
        )
    
    def toJSON(self) -> dict:
        return dict(
            tasks=[t.toJSON() for t in self.tasks]
        )
    
    def get_task(self, name: str) -> Task | None:
        return next((t for t in self.tasks if t.name == name), None)

    def add_task(self, task_name: str) -> Task:
        _task = next((t for t in self.tasks if t.name == task_name), None)

        if _task:
            return _task
        
        self.tasks.append(
            Task(
                name=task_name,
                skills=[]
            )
        )

        return self.tasks[-1]
    
    def add_skill(self, task_name: str, skill: Skill, parent: str = "") -> bool:
        task = self.get_task(task_name)

        if not task:
            task = self.add_task(task_name)

        if parent:
            return self._add_to_skill(task.skills, skill, parent)
        
        task.skills.append(skill)
        return True
    
    def _add_to_skill(self, skills: list[Skill], skill: Skill, parent: str) -> bool:
        for skill in skills:
            if skill.name == parent:
                skill.children.append(skill)
                return True
            
            if self._add_to_skill(skill.children, skill, parent):
                return True
            
        return False

