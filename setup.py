from setuptools import setup
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='paamon',
      version='0.1.0',
      packages=['paamon'],
      install_requires=requirements,
      entry_points={'console_scripts': ['flatpak-pypi = paamon.__main__:main']})
