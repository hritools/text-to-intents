import setuptools


VERSION = '0.1'


with open('README.md', 'r') as f:
    long_description = f.read()


with open('requirements.txt') as f:
    required = f.read().splitlines()


setuptools.setup(
    name='TextToIntents-Ru',
    python_requires='~=3.7',
    version=VERSION,
    author='Vlad Kurenkov',
    author_email='v.kurenkov@nnopolis.ru',
    description='Semantic Parsing for Russian language',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://cordelianew.university.innopolis.ru/gitea/hri/text-to-intents.git',
    packages=setuptools.find_packages(),
    install_requires=required,
)