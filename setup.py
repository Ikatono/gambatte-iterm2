from setuptools import Extension, setup


gambatte_extension = Extension(
    "gambaterm._gambatte",
    language="c++",
    libraries=["gambatte"],
    extra_compile_args=["-Ilibgambatte"],
    extra_link_args=["-Llibgambatte"],
    sources=["ext/_gambatte.pyx"],
)


setup(
    name="gambaterm",
    version="0.1.0",
    packages=["gambaterm"],
    setup_requires=["setuptools>=18.0", "cython", "numpy"],
    ext_modules=[gambatte_extension],
    install_requires=[
        "numpy",
        "asyncssh",
        "sounddevice",
        "samplerate",
        "xlib; sys_platform == 'linux'",
    ],
    tests_require=["pytest"],
    python_requires=">=3.6",
    description="A terminal frontend for gambatte game boy color emulator ",
    url="https://github.com/vxgmichel/gambatte-terminal",
    license="GPLv3",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    author="Vincent Michel",
    author_email="vxgmichel@gmail.com",
)
