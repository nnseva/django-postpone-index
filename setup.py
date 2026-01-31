from setuptools import setup, Extension

setup(
    name='django-postpone-index',
    use_scm_version=True,
    python_requires='>=3.10',
    # build-time requirements are declared in pyproject.toml
    description='Postpone index creation to provide Zero Downtime Migration feature',
    author='Vsevolod Novikov',
    author_email='nnseva@gmail.com',
    url='https://github.com/nnseva/django-postpone-index',
    project_urls={
        'Source': 'https://github.com/nnseva/django-postpone-index',
        'Issues': 'https://github.com/nnseva/django-postpone-index/issues',
    },
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Programming Language :: Python :: 3.15',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Topic :: Software Development :: Libraries',
    ],
    keywords=[
        'zero-downtime-migration',
        'django',
        'migration',
        'zero-downtime',
        'downtime',
        'postgres',
        'postgresql',
    ],
    license='LGPLv3',
    packages=['postpone_index'],
)
