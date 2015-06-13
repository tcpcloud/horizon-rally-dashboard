
from horizon import tables


class FilterAction(tables.FilterAction):

    needs_preloading = True

    def filter_number_data(self, table, data, filter_string):
        return self.filter(table, data, filter_string)

    def filter_timestamp_data(self, table, data, filter_string):
        return self.filter(table, data, filter_string)

    def filter(self, table, data, filter_string):
        q = filter_string.lower()

        def comp(obj):
            if isinstance(obj, dict):
                for key, value in obj.iteritems():
                    if q in str(obj.get(key, "")).lower():
                        return True
            if isinstance(obj, object):
                try:
                    for prop in obj._meta.fields:
                        name = prop.name
                        if q in str(obj.__dict__[name]):
                            return True
                except Exception:
                    # swallowed exception
                    pass
            return False

        return filter(comp, data)
