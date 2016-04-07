SECRET_KEY = 'test'

INSTALLED_APPS = (
    'task_monitor',
    'tests',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
