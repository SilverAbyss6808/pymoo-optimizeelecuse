from setuptools import find_packages, setup

# print(find_packages("C:\\Users\\baxte\\anaconda3\\envs\\pymoo-optimizeelecuse\\Lib\\site-packages"))

setup(
    name='poeu-scripts',
    packages=find_packages('C:\\Users\\baxte\\anaconda3\\envs\\pymoo-optimizeelecuse\\Lib\\site-packages'),
    package_dir={'':'C:\\Users\\baxte\\anaconda3\\envs\\pymoo-optimizeelecuse\\Lib\\site-packages'},
    version='0.1.1',
    description='Helper scripts for the electricity optimization game.',
    author='Lila Baxter',
)