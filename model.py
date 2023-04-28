import os
import time
import traceback

from arelle import FileSource as FileSourceFile, PluginManager
from arelle.Cntlr import Cntlr
from arelle.CntlrCmdLine import filesourceEntrypointFiles
from arelle.FileSource import FileSource
from arelle.ModelXbrl import ModelXbrl

from parse_facts import process
from utils import move_file_to_parsed, move_file_to_error, _path_to_language

# specify file ending zip
FILE_ENDING_ZIP = ".zip"

# specify path to archives
# here testing or training archive should be stated
PATH_ARCHIVES = archives = os.path.join(".", "archives_training")
PATH_PARSED = parsed = os.path.join(".", "parsed")
PATH_FAILED = parsed = os.path.join(".", "error")

# adapted from pyesef
# Define a controller for Arelle
class Controller(Cntlr):  # type: ignore
    """Controller."""

    def __init__(self) -> None:
        """Init controller with logging."""
        super().__init__(logFileName="logToPrint", hasGui=False)

# adapted from pyesef
# load into xbrl model
def _load_esef_xbrl_model(zip_file_path: str, cntlr: Controller) -> ModelXbrl:
    #model_xbrl = None
    """Load a ModelXbrl from a file path."""
    try:
        file_source: FileSource = FileSourceFile.openFileSource(
            zip_file_path,
            cntlr,
            checkIfXmlIsEis=False,
        )

        # Find entrypoint files
        _entrypoint_files = filesourceEntrypointFiles(
            filesource=file_source,
            entrypointFiles=[{"file": zip_file_path}],
        )

        # This is required to correctly populate _entrypointFiles
        for plugin_xbrl_method in PluginManager.pluginClassMethods(
            "CntlrCmdLine.Filing.Start"
        ):
            plugin_xbrl_method(
                cntlr,
                None,
                file_source,
                _entrypoint_files,
                sourceZipStream=None,
                responseZipStream=None,
            )
        _entrypoint = _entrypoint_files[0]
        _entrypoint_file = _entrypoint["file"]
        file_source.select(_entrypoint_file)
        cntlr.entrypointFile = _entrypoint_file

        # Load plugin
        cntlr.modelManager.validateDisclosureSystem = True
        cntlr.modelManager.disclosureSystem.select("esef")
        model_xbrl = cntlr.modelManager.load(
            file_source,
            "Loading",
            entrypoint=_entrypoint,
        )

        file_source.close()
        return model_xbrl
    except Exception as exc:
        raise OSError("File not loaded due to ", exc) from exc

# inspired by pyesef
# will load into xbrl model and 
# extend the facts list
def read_and_save_filings():
    start = time.time()
    idx = 0
    cntlr = Controller()

    PluginManager.addPluginModule("validate/ESEF")
    # iterate over the folders in archives
    for subdir, _, files in os.walk(PATH_ARCHIVES):
            cntlr.addToLog(f"Parsing {len(files)} reports in folder {subdir}")
            # iterate over files in folder
            for file in files:
                facts = []
                idx +=1
                cntlr.addToLog(f"Working on file {file}")
                _error: bool = False
                error_message: str | None = None

                zip_file_path = subdir + os.sep + file

                if zip_file_path.endswith(FILE_ENDING_ZIP):
                    # Load zip-file into a ModelXbrl instance
                    try:
                        model_xbrl: ModelXbrl = _load_esef_xbrl_model(
                            zip_file_path=zip_file_path,
                            cntlr=cntlr,
                        )
                        # extend the array with the facts of the model
                        
                        facts.extend(model_xbrl.facts) 
                        process(facts)


                        #ModelXbrl=None
                        model_xbrl.close()
                        model_xbrl = None
                    except Exception as exc:
                        error_message = "".join(
                            traceback.TracebackException.from_exception(exc).format()
                        )
                        _error = True
                    language = _path_to_language(subdir)
                    if _error and error_message is not None:
                        move_file_to_error(zip_file_path=zip_file_path, language=language)
                        cntlr.addToLog(f"Moved file to error folder due to {error_message}")
                    else: 
                        move_file_to_parsed(zip_file_path=zip_file_path, language=language)
                        cntlr.addToLog("Moved files to parsed folder")
         
    end = time.time()
    total_time = end - start
    cntlr.addToLog(f"Loaded {idx} XBRL-files in {total_time}s")
    cntlr.addToLog("Finished loading")
    cntlr.close()
