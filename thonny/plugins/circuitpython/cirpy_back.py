import os.path
import sys
from logging import getLogger
from typing import List, Optional

# make sure thonny folder is in sys.path (relevant in dev)
thonny_container = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if thonny_container not in sys.path:
    sys.path.insert(0, thonny_container)


from thonny.plugins.micropython.bare_metal_backend import (
    BareMetalMicroPythonBackend,
    launch_bare_metal_backend,
)

# Can't use __name__, because it will be "__main__"
logger = getLogger("thonny.plugins.micropython.cirpy_backend")

_ENTER_REPL_PHRASES = [
    "Press any key to enter the REPL. Use CTRL-D to reload.",
    "Appuyez sur n'importe quelle touche pour utiliser le REPL. Utilisez CTRL-D pour relancer.",
    "Presiona cualquier tecla para entrar al REPL. Usa CTRL-D para recargar.",
    "Drücke eine beliebige Taste um REPL zu betreten. Drücke STRG-D zum neuladen.",
    "Druk een willekeurige toets om de REPL te starten. Gebruik CTRL+D om te herstarten.",
    "àn rèn hé jiàn jìn rù REPL. shǐ yòng CTRL-D zhòng xīn jiā zǎi ."
    "Tekan sembarang tombol untuk masuk ke REPL. Tekan CTRL-D untuk memuat ulang.",
    "Pressione qualquer tecla para entrar no REPL. Use CTRL-D para recarregar.",
    "Tryck på valfri tangent för att gå in i REPL. Använd CTRL-D för att ladda om.",
    "Нажмите любую клавишу чтобы зайти в REPL. Используйте CTRL-D для перезагрузки.",
]

_AUTO_RELOAD_PHRASES = [
    "Auto-reload is on. Simply save files over USB to run them or enter REPL to disable.",
    "Auto-chargement activé. Copiez ou sauvegardez les fichiers via USB pour les lancer ou démarrez le REPL pour le désactiver.",
    "Auto-reload habilitado. Simplemente guarda los archivos via USB para ejecutarlos o entra al REPL para desabilitarlos.",
    "Automatisches Neuladen ist aktiv. Speichere Dateien über USB um sie auszuführen oder verbinde dich mit der REPL zum Deaktivieren.",
    "L'auto-reload è attivo. Salva i file su USB per eseguirli o entra nel REPL per disabilitarlo.",
    "Auto-reload be on. Put yer files on USB to weigh anchor, er' bring'er about t' the REPL t' scuttle.",
    "Auto-herlaad staat aan. Sla bestanden simpelweg op over USB om uit te voeren of start REPL om uit te schakelen.",
    "Ang awtomatikong pag re-reload ay ON. i-save lamang ang mga files sa USB para patakbuhin sila o pasukin ang REPL para i-disable ito.",
    "Zìdòng chóngxīn jiāzài. Zhǐ xū tōngguò USB bǎocún wénjiàn lái yùnxíng tāmen huò shūrù REPL jìnyòng.",
    "Auto-reload aktif. Silahkan simpan data-data (files) melalui USB untuk menjalankannya atau masuk ke REPL untukmenonaktifkan.",
    "Samo-przeładowywanie włączone. Po prostu zapisz pliki przez USB aby je uruchomić, albo wejdź w konsolę aby wyłączyć.",
    "O recarregamento automático está ativo. Simplesmente salve os arquivos via USB para executá-los ou digite REPL para desativar.",
    "Autoladdning är på. Spara filer via USB för att köra dem eller ange REPL för att inaktivera.",
    "Автоматическая перезагрузка включена. Просто сохрани файл по USB или зайди в REPL чтобы отключить.",
]


class CircuitPythonBackend(BareMetalMicroPythonBackend):
    def _clear_repl(self):
        """
        CP runs code.py after soft-reboot even in raw repl.
        At the same time, it re-initializes VM and hardware just by switching
        between raw and friendly REPL (tested in CP 6.3 and 7.1)
        """
        logger.info("Creating fresh REPL for CP")
        self._ensure_normal_mode()
        self._ensure_raw_mode()

    def _transform_output(self, data, stream_name):
        # Any keypress wouldn't work in Thonny's shell
        for phrase in _ENTER_REPL_PHRASES + _AUTO_RELOAD_PHRASES:
            data = data.replace(phrase + "\r\n", "").replace(phrase + "\n", "")

        return data

    def _output_warrants_interrupt(self, data):
        data = data.strip()
        for phrase in _ENTER_REPL_PHRASES:
            if data.endswith(phrase.encode("utf-8")):
                return True

        return False

    def _get_sys_path_for_analysis(self) -> Optional[List[str]]:
        return [
            os.path.join(os.path.dirname(__file__), "api_stubs"),
        ]


if __name__ == "__main__":
    launch_bare_metal_backend(CircuitPythonBackend)
