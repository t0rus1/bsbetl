import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="shwpy-bsbetl-t0rus1",
    version="1.1.92dev0",
    author="leon van dyk & gunther lu",
    author_email="leonvandyk@gmail.com",
    description="BSB Extract Transform Load Utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/t0rus1/shwpy",
    data_files=[
        ('../venv/Lib/site-packages/bsbetl',
         ['bsbetl/config_runtime.json', 'bsbetl/config_settings.json']),
        ('../venv/Lib/site-packages/bsbetl/assets',
         ['bsbetl/assets/custom-script.js', 'bsbetl/assets/favicon.ico', 'bsbetl/assets/header.css', 'bsbetl/assets/tabs.css', 'bsbetl/assets/typography.css', 'bsbetl/assets/scrollbtn.css']),
        ('../venv/Lib/site-packages/bsbetl/xtras',
         ['bsbetl/xtras/MasterShareDictionary.csv', 'bsbetl/xtras/Default.shl']),
        ('../venv/Lib/site-packages/bsbetl/scripts',
         ['bsbetl/scripts/w.bat']),
    ],
    packages=setuptools.find_packages(),  # ['bsbetl'],
    package_data={},
    install_requires=['numpy', 'pandas', 'click', 'tkcalendar',
                      'dash', 'Flask', 'requests', 'requests_ntlm', 'pluralizer', 'tables', 'openpyxl'],
    entry_points={
        'console_scripts': ['bsbetl = bsbetl.cli:start']
    },
    license='unlicense',
    # classifiers=[
    #     "Programming Language :: Python :: 3",
    #     #"License :: OSI Approved :: MIT License",
    #     "Operating System :: Microsoft :: Windows :: Windows 10"
    # ],
    python_requires='>=3.8',
)
