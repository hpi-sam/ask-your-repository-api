from application.models import Artifact
from application.models.artifact_builder import ArtifactBuilder

class ArtifactFactory:
    @classmethod
    def create_artifact(cls, user_tags=[], *args, **kwargs):
        artifact = cls.build_artifact(*args, **kwargs).save()

        if user_tags:
            builder = ArtifactBuilder.for_artifact(artifact)
            builder.update_with(user_tags=user_tags)

    @classmethod
    def build_artifact(cls, id_='abc', file_url='abc'):
        return Artifact(id_=id_, file_url=file_url)
