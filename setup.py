from setuptools import setup, find_packages

setup(
    name="saki-market-game",
    version="1.0.0",
    author="Behnam Saki",
    author_email="saki.pocc@gmail.com",
    description="A decentralized energy market simulation using Proof of Contribution Competition (PoCC)",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Tart-saki/saki-market-game-whitepaper",
    packages=find_packages(),  # Auto-discovers all packages like saki_market_game
    include_package_data=True,
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib",
        "openpyxl",  # for Excel output
    ],
    entry_points={
        "console_scripts": [
            "saki-market = saki_market_game.main:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires=">=3.8",
)
