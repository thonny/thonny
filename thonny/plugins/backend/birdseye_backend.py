import os
import sys
from thonny.backend import get_vm, Executor
import webbrowser


def _cmd_Birdseye(cmd):
    vm = get_vm()
    vm.switch_env_to_script_mode(cmd)
    return vm._execute_file(cmd, BirdsEyeRunner)


class BirdsEyeRunner(Executor):
    def execute_source(self, source, filename, mode, ast_postprocessors):
        assert mode == "exec"
        # ignore ast_postprocessors, because birdseye requires source

        if isinstance(source, bytes):
            source = source.decode("utf-8")

        import __main__  # @UnresolvedImport
        global_vars = __main__.__dict__

        try:
            sys.meta_path.insert(0, self)
            self._vm._install_custom_import()

            # Following is a trick, which allows importing birdseye in the backends,
            # which doesn't have it installed (provided it is installed for frontend Python)
            orig_sys_path = sys.path
            try:
                sys.path = orig_sys_path + self._vm._frontend_sys_path
                from birdseye.bird import eye
            finally:
                sys.path = orig_sys_path

            eye.exec_string(source, filename, globs=global_vars, locs=global_vars, deep=True)
            port = os.environ.get("BIRDSEYE_PORT", "7777")
            webbrowser.open_new_tab('http://localhost:%s/ipython_call/' % port
                                    + eye._last_call_id)
            return {"context_info": "after normal execution"}
        except Exception:
            return {"user_exception": self._vm._prepare_user_exception()}
        finally:
            del sys.meta_path[0]
            if hasattr(self._vm, "_original_import"):
                self._vm._restore_original_import()


def load_plugin():
    get_vm().add_command("Birdseye", _cmd_Birdseye)
