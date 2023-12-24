

class HistoricalDataRouter:

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'historical_data':
            return 'historical_data'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'historical_data':
            return 'historical_data'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        # Allow any relation if both models are part of the historical_data app
        if obj1._meta.app_label == 'historical_data' and obj2._meta.app_label == 'historical_data':
            return True
        # No opinion if neither object is part of the historical_data app
        elif 'historical_data' not in [obj1._meta.app_label, obj2._meta.app_label]:
            return None
        # Block relations if one object is part of the historical_data app and the other isn't
        else:
            return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == 'historical_data':
            return app_label == 'historical_data'
        elif app_label == 'historical_data':
            return False
        return None
