from .elastic.elastic_syncer import ElasticSyncer
import os

from pathlib import Path
from flask import current_app

class ArtifactDeletor:
    def __init__(self, artifact):
        self.artifact = artifact

    def delete(self):
        ElasticSyncer.for_artifact(self.artifact).delete()
        filename_without_ext = os.path.splitext(self.artifact.file_url)[0]
        self._delete_files_starting_with(filename_without_ext)


    def _delete_files_starting_with(self, start_string):
        for p in Path(current_app.config["UPLOAD_FOLDER"]).glob(f"{start_string}*"):
            p.unlink()