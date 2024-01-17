from bson.objectid import ObjectId

class PydanticObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, obj):
        if not isinstance(v, ObjectId):
            raise TypeError('ObjectId required')
        return str(v)