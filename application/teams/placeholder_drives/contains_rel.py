from neomodel import StructuredRel, StringProperty

from application.model_mixins import DefaultPropertyMixin, DefaultHelperMixin


class ContainsRel(StructuredRel, DefaultPropertyMixin, DefaultHelperMixin):
    gdrive_file_id = StringProperty(required=True)
