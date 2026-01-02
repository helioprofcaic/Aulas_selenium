from setuptools import setup, find_packages

setup(
    name='assistente-aulas',
    version='1.0.0',
    author='Helio Lima',
    author_email='raimundo.helio@professor.edu.pi.gov.br',
    description='Automação de registro de aulas para o Portal Seduc-PI.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    py_modules=['app'],
    include_package_data=True,
    keywords=['automacao', 'selenium', 'seduc', 'professor', 'registro de aulas'],
    install_requires=[
        'selenium',
        'webdriver-manager',
        'python-dateutil',
        'pyautogui',
        'opencv-python',
    ],
    entry_points={
        'console_scripts': [
            'assistente-aulas=app:main',
        ],
    },
)