import setuptools 

if __name__ == "__main__":
    setuptools.setup(
        name='weather',
        version='0.1.0',
        packages=setuptools.find_packages(),
        entry_points={
            'console_scripts':[
                'weather = weather.main:main',
            ],
        },
    )
