from setuptools import setup

setup(
    name='openai-utils',
    version='0.1.0',
    py_modules=['openai_utils'],  # Specify the module directly
    install_requires=[
        'openai',
        'python-dotenv',
    ],
    entry_points={
        'console_scripts': [
            # Add command line scripts here if needed
        ],
    },
    author='Fernando Wittmann',
    author_email='fernando.wittmann@gmail.com',
    description='A utility package for OpenAI chat client',
    url='https://github.com/wittmannf/openai-utils',  # Update with your repo URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)
