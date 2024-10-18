import os
import shutil
import uuid

import panel as pn

from atap_corpus_loader import CorpusLoader

pn.extension('filedropper', notifications=True)


ROOT_DIR: str = "user_root"


def get_user_directory(session_context):
    session_id = str(uuid.uuid4())
    user_dir = os.path.join(ROOT_DIR, session_id)

    os.makedirs(user_dir, exist_ok=True)

    session_context.user_dir = user_dir
    return user_dir


def cleanup_dir(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)


def cleanup(session_context):
    user_dir = session_context.user_dir
    cleanup_dir(user_dir)


def user_view():
    pn.state.on_session_destroyed(cleanup)
    session_context = pn.state.curdoc.session_context
    user_dir = get_user_directory(session_context)

    corpus_loader: CorpusLoader = CorpusLoader(user_dir, include_meta_loader=True, include_oni_loader=True,
                                               run_logger=True)

    return corpus_loader.servable()


def runserver():
    pn.serve(user_view)


if __name__ == "__main__":
    runserver()
