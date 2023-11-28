

class HistoricalCryptoDataRouter:

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'historical_crypto_data':
            return 'historical_crypto_data'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'historical_crypto_data':
            return 'historical_crypto_data'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        if (
            obj1._meta.app_label == 'historical_crypto_data'
            and
            obj2._meta.app_label == 'historical_crypto_data'
        ):
            return True
        elif (
            'historical_crypto_data' not in [
                obj1._meta.app_label,
                obj2._meta.app_label
            ]
        ):
            return False
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == 'historical_crypto_data':
            return app_label == 'historical_crypto_data'
        elif app_label == 'historical_crypto_data':
            return False
        return None
