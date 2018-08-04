import json


class BaseField:

    def __init__(self, required=False, unique=False):
        self.value = None
        self.required = required
        self.unique = unique
        self.index = self.unique

    def validate(self, value):
        if self.required and value is None:
            raise ValueError(f'Field {self.__class__.__name__} is required.')
        else:
            return value

    def __get__(self, obj, type=None):
        return self.value

    def __setter__(self, obj, value):
        self.value = value


class CharField(BaseField):

    def validate(self, value):
        return super().validate(value)


class IntegerField(BaseField):

    def validate(self, value):
        return super().validate(int(value))


class FloatField(BaseField):

    def validate(self, value):
        return super().validate(float(value))


class JSONField(BaseField):

    def validate(self, value):
        try:
            json.dumps(value)
        except ValueError as e:
            raise ValueError 
        return super().validate(value)


class BooleanField(BaseField):

    def validate(self, value):
        return super().validate(bool(value))


class ObjectIdField(BaseField):

    def validate(self, value):
        return super().validate(str(value))
