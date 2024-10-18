import os
import shutil

import panel as pn

from atap_corpus_loader import CorpusLoader

pn.extension('filedropper', notifications=True)


ROOT_DIR: str = "corpus_files"


def cleanup_dir(directory):
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
            except Exception:
                continue


def cleanup_session(session_context):
    cleanup_dir(ROOT_DIR)


def user_view():
    pn.state.on_session_destroyed(cleanup_session)
    corpus_loader: CorpusLoader = CorpusLoader(ROOT_DIR,
                                               include_meta_loader=True,
                                               include_oni_loader=True,
                                               run_logger=True)

    return corpus_loader.servable()
