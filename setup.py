from setuptools import setup, find_packages

setup(
    name="chatbot-app",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "streamlit",
        "together",
        "pytest",
        "python-dotenv",
    ],
    entry_points={
        'console_scripts': [
            'chatbot-app=run_app:main',
        ],
    },
    author="Chad Norwood",
    author_email="chad@chadnorwood.com",
    description="A Streamlit chatbot application using Together AI",
    keywords="chatbot, streamlit, together-ai",
    url="https://github.com/chadn/chatbot7",
) 