from datetime import datetime

class SerializerMixin:
    def to_dict(self, exclude=None, include=None, _depth=0, _max_depth=2):
        """Enhanced serialization with depth control"""
        if exclude is None:
            exclude = getattr(self, 'SERIALIZE_EXCLUDE', [])
        if include is None:
            include = getattr(self, 'SERIALIZE_INCLUDE', [])
            
        if _depth > _max_depth:
            return None
            
        data = {}
        for column in self.__table__.columns:
            if column.name not in exclude:
                value = getattr(self, column.name)
                if isinstance(value, datetime):
                    value = value.isoformat()
                elif hasattr(value, 'value'):  # Handle Enum types
                    value = value.value
                data[column.name] = value
        
        # Handle relationships
        for rel in include:
            if rel in exclude:
                continue
                
            if hasattr(self, rel):
                relationship = getattr(self, rel)
                if relationship is None:
                    data[rel] = None
                elif isinstance(relationship, list):
                    data[rel] = [
                        item.to_dict(
                            _depth=_depth+1,
                            _max_depth=_max_depth
                        ) 
                        for item in relationship
                        if item is not None
                    ]
                else:
                    data[rel] = relationship.to_dict(
                        _depth=_depth+1,
                        _max_depth=_max_depth
                    ) if relationship is not None else None
        
        return data