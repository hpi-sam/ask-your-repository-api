from neomodel import match, Traversal
from .artifact import Artifact
from ..date.day import Day


class ArtifactRecommendator:
    def __init__(self, artifact):
        self.artifact = artifact

    def _get_scores_for_relationship(self, rel):
        relationships = getattr(self.artifact, rel)
        if len(relationships) == 0: return {}

        scores = {}

        for end_node in relationships:
            for artifact in end_node.artifacts:
                if artifact.id_ == self.artifact.id_: continue

                if artifact.id_ in scores:
                    scores[artifact.id_] += 1
                else:
                    scores[artifact.id_] = 1

        return {id: float(score) / len(relationships) for id, score in scores.items()}

    def _get_scores_for_date(self):
        day = self.artifact.day.single()
        traversal_definition = dict(node_class=Artifact, direction=match.EITHER,
                                    relation_type=None, model=None)
        traversal = Traversal(day, "artifacts_on_day", traversal_definition)
        scores = {}

        for artifact in traversal.all():
            if artifact.id_ == self.artifact.id_: continue
            scores[artifact.id_] = 1

        return scores

    def run(self, limit):
        categories = {
            "persons": self._get_scores_for_relationship('persons'),
            "locations": self._get_scores_for_relationship('locations'),
            "labels": self._get_scores_for_relationship('label_tags'),
            "text": self._get_scores_for_relationship('text_tags'),
            "date": self._get_scores_for_date(),
        }

        total_scores = {}

        for category, category_scores in categories.items():
            for artifact_id, score in category_scores.items():
                if not artifact_id in total_scores:
                    artifact = Artifact.find_by(id_=artifact_id)
                    total_scores[artifact_id] = artifact
                    total_scores[artifact_id].recommendation_scores = { "total": 0 }

                total_scores[artifact_id].recommendation_scores[category] = score
                total_scores[artifact_id].recommendation_scores["total"] += score

        recommendations = sorted(total_scores.values(), key=lambda a: a.recommendation_scores["total"], reverse=True)

        return recommendations[0:limit]
