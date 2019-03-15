# -*- coding:utf-8 -*-
#
# Copyright (C) 2019 [Victor Torre](https://github.com/ehooo)
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import bandit
from bandit.core import test_properties as test


@test.checks('Call')
@test.test_id('DJ-POPEN')
def django_popen_wrapper_used(context):
    """**DJ-POPEN: Potential Code execution via call to subprocess.Popen**

    .. seealso::
     - https://github.com/django/django/blob/master/django/core/management/utils.py
    """
    description = "popen_wrapper call to subprocess.Popen with shell=False"
    if context.is_module_imported_like('django.core.management.utils'):
        if context.call_function_name == 'popen_wrapper':
            return bandit.Issue(
                severity=bandit.LOW,
                confidence=bandit.HIGH,
                text=description
            )
