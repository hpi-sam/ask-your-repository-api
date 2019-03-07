"""Cleans up Properties for Artifact creation."""


class PropertyBuilder:
    """Describe a PropertyBuilder."""
    RELATIONSHIP_TYPES = ['tags', 'user_tags', 'label_tags', 'text_tags', 'team_id', 'user_id']
    NODE_TYPES = ['file_url', 'file_date']

    def __init__(self, **properties):
        self.__properties = properties
        self.__relationship_properties = None
        self.__node_properties = None

    @property
    def properties(self):
        """Return full properties."""
        return self.__properties

    @property
    def relationship_properties(self):
        """Return properties describing relationships."""
        if self.__relationship_properties is None:
            self._make_relationship_properties()
        return self.__relationship_properties

    def _make_relationship_properties(self):
        """Lazy initialize relationship properties."""
        self.__relationship_properties = {}
        for k, v in self.properties.items():
            if k in self.RELATIONSHIP_TYPES:
                self.__relationship_properties[k] = v

    @property
    def node_properties(self):
        """Return node properties."""
        if self.__node_properties is None:
            self._make_node_properties()
        return self.__node_properties

    def _make_node_properties(self):
        """Lazy initialize node properties."""
        self.__node_properties = {}
        for k, v in self.properties.items():
            if k in self.NODE_TYPES:
                self.__node_properties[k] = v
