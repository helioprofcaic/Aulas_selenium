from setuptools import setup, find_packages

setup(
    name='assistente-aulas',
    version='1.0.0',
    author='Helio Lima',
    author_email='raimundo.helio@professor.edu.pi.gov.br',
    description='Ferramenta de linha de comando para automação e gerenciamento de aulas.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    py_modules=['app'],
    include_package_data=True,
    install_requires=[
        'selenium',
        'pyperclip',
        'pyautogui',
        'opencv-python',
    ],
    entry_points={
        'console_scripts': [
            'assistente-aulas=app:main',
        ],
    },
)