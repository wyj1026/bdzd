from setuptools import setup, find_packages

setup(
    name="bdzd",
    version="0.1",
    description="Get chinese answers in command line",
    long_description=" ",
    author="Yijie Wang",
    author_email="wangyijieim@outlook.com",
    liscence="MIT",
    packages=find_packages(),
    entry_points={
        'console_scripts':[
            'bdzd = bdzd.bdzd:command_line_executor',
        ]
    },
    install_requires={
        'click',
        'pyquery',
        'requests',
        'requests-cache'
    }
)
