from neomodel import StructuredRel, FloatProperty

from application.model_mixins import DefaultPropertyMixin, DefaultHelperMixin


class LabeledWithRel(StructuredRel, DefaultPropertyMixin, DefaultHelperMixin):
    score = FloatProperty()
    topicality = FloatProperty()
