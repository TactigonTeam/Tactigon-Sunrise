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

package_name = 'camera_tracking'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(include=['camera_tracking', 'camera_tracking.*']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Stefano Barbareschi',
    maintainer_email='developer@nextind.eu',
    description='Track pointing',
    license='Apache 2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'camera_tracking = camera_tracking.main:main',
        ],
    },
)