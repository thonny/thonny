from abc import ABC, abstractmethod

import minny.common
import thonny.common
from minny.target import ProperTargetManager

from logging import getLogger

logger = getLogger(__name__)


class MicroPythonProjectManager(ABC):
    @abstractmethod
    def deploy(self, before_run: bool) -> None: ...


class MinnyProjectManager(MicroPythonProjectManager):
    def __init__(self, project_path: str, tmgr: ProperTargetManager):
        from minny.project import ProjectManager
        from minny.tracking import Tracker
        from minny.compiling import Compiler

        tracker = Tracker(tmgr)
        compiler = Compiler(tmgr)
        self._project_path = project_path
        self._pmgr = ProjectManager(
            project_path,
            tmgr,
            tracker,
            compiler,
        )

    def deploy(self, before_run: bool) -> None:
        logger.info(f"Deploying project {self._project_path}")
        try:
            self._pmgr.deploy(except_main=before_run)
        except minny.common.ProjectError as e:
            raise thonny.common.UserError(f"Project error: {e}") from e
        except minny.common.UserError as e:
            raise thonny.common.UserError(str(e)) from e
        logger.info(f"Done deploying project {self._project_path}")


class BelayProjectManager(MicroPythonProjectManager):
    def deploy(self, before_run: bool) -> None:
        pass


def create_project_manager(
    manager_name: str, project_path: str, tmgr: ProperTargetManager
) -> MicroPythonProjectManager:
    # TODO: validate project type and print warning if not matching

    if manager_name == "Minny":
        return MinnyProjectManager(project_path, tmgr)
    elif manager_name == "Belay":
        return BelayProjectManager(project_path, tmgr)
    else:
        raise ValueError(f"Unknown project manager {manager_name}")
