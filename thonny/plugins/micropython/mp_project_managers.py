from abc import ABC, abstractmethod

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
        logger.debug(f"Deploying project {self._project_path}")
        self._pmgr.deploy(except_main=before_run)
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
