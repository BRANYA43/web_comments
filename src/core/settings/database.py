from core.settings.environments import envs

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': envs.db.name,
        'HOST': envs.db.host,
        'PORT': envs.db.port,
        'USER': envs.db.user,
        'PASSWORD': envs.db.password,
        'TEST': {
            'NAME': 'testing',
        },
    }
}
