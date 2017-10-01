#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ["YaDiskObject"]

class YaDiskObject(object):
    def __init__(self, field_types=None):
        if field_types is None:
            field_types = {}

        self.FIELD_TYPES = {}
        self.FIELDS = {}
        self.set_field_types(field_types)

    def set_field_types(self, field_types):
        self.FIELD_TYPES = field_types

        for field in field_types.keys():
            self[field] = None

    def set_field_type(self, field, type):
        self.FIELD_TYPES[field] = type
        self[field] = None

    def remove_field(self, field):
        self.FIELDS.pop(field)
        self.FIELD_TYPES.pop(field)

    def import_fields(self, source_dict):
        if source_dict is not None:
            for field in self.FIELDS:
                self[field] = source_dict.get(field)

    def __setattr__(self, attr, value):
        if attr in ("FIELDS", "FIELD_TYPES"):
            self.__dict__[attr] = value
            return
        elif attr not in self.FIELD_TYPES:
            raise AttributeError("Unknown attribute: %r" % (attr,))

        datatype = self.FIELD_TYPES[attr]
        self.FIELDS[attr] = datatype(value) if value is not None else None

    def __getattr__(self, attr):
        if attr in ("FIELDS", "FIELD_TYPES"):
            return self.__dict__[attr]
        elif attr not in self.FIELD_TYPES:
            raise AttributeError("Unknown attribute: %r" % (attr,))

        return self.FIELDS[attr]

    def __getitem__(self, key):
        return self.FIELDS[key]

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def __delitem__(self, key):
        del self.FIELDS[key]

    def __iter__(self):
        return iter(self.FIELDS)

    def __len__(self):
        return len(self.FIELDS)

    def __repr__(self, initial_indent_size=0):
        return "<%s%r>" % (self.__class__.__name__, self.FIELDS)

