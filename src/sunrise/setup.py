#********************************************************************************
# Copyright (c) 2025 Next Industries s.r.l.
#
# This program and the accompanying materials are made available under the
# terms of the Apache 2.0 which is available at http://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
#
# Contributors:
# Massimiliano Bellino
# Stefano Barbareschi
#********************************************************************************

from setuptools import find_packages, setup

package_name = 'sunrise'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(include=['sunrise', 'sunrise.*']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='robot',
    maintainer_email='developer@nextind.eu',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest'
        ],
    },
    entry_points={
        'console_scripts': [
            'mission_controller = sunrise.mission_controller.main:main',
            'sunrise_bridge = sunrise.sunrise_bridge.main:main',
            'sunrise_braccio = sunrise.sunrise_braccio.main:main',
            'sunrise_comau = sunrise.sunrise_comau.main:main',
            'sunrise_tactigon = sunrise.sunrise_tactigon.main:main',
            'sunrise_mock = sunrise.sunrise_tactigon_mock.main:main'
        ],
    },
)
