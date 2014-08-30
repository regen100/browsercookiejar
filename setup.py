from setuptools import setup, find_packages

setup(
    name='browsercookiejar',
    version='0.1',
    author='Regen',
    author_email='git@exadge.com',
    description='CookieJar for browsers',
    long_description=(open('README.rst').read() + '\n\n' +
                      open('CHANGES.rst').read()),
    url='https://github.com/regen100/browsercookiejar',
    platforms=['Linux', 'Windows'],
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Topic :: Internet :: WWW/HTTP :: Browsers',
    ],
    packages=find_packages(),
)
