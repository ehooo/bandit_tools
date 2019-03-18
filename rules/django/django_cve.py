# -*- coding:utf-8 -*-
#
# Copyright (c) 2017
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

import ast
import bandit
from bandit.core import test_properties as test

FORMAT_SETTINGS = [
    'DECIMAL_SEPARATOR',
    'THOUSAND_SEPARATOR',
    'NUMBER_GROUPING',
    'FIRST_DAY_OF_WEEK',
    'MONTH_DAY_FORMAT',
    'TIME_FORMAT',
    'DATE_FORMAT',
    'DATETIME_FORMAT',
    'SHORT_DATE_FORMAT',
    'SHORT_DATETIME_FORMAT',
    'YEAR_MONTH_FORMAT',
    'DATE_INPUT_FORMATS',
    'TIME_INPUT_FORMATS',
    'DATETIME_INPUT_FORMATS',
]


@test.checks('Call')
@test.test_id('CVE-2012-3443')
def imagefield_used(context):
    """**CVE-2012-3443: Test for the use of ImageField**

    The django.forms.ImageField class in the form system in Django before
    1.3.2 and 1.4.x before 1.4.1 completely decompresses image data during
    image validation, which allows remote attackers to cause a denial of
    service (memory consumption) by uploading an image file.

    .. seealso::

     - https://www.cvedetails.com/cve/CVE-2012-3443/
     - https://www.djangoproject.com/weblog/2012/jul/
        30/security-releases-issued/
     - https://github.com/django/django/commit/
        b2eb4787a0fff9c9993b78be5c698e85108f3446

    .. versionadded:: X.X.X

    """
    description = "Use of ImageField affected by CVE-2012-3443."
    if context.is_module_imported_like('django.forms'):
        if context.call_function_name == 'ImageField':
            return bandit.Issue(
                severity=bandit.MEDIUM,
                confidence=bandit.LOW,
                text=description
            )


@test.checks('Call')
@test.test_id('CVE-2012-3444')
def get_image_dimensions_used(context):
    """**CVE-2012-3444: Test for the use of get_image_dimensions**

    The get_image_dimensions function in the image-handling functionality in
    Django before 1.3.2 and 1.4.x before 1.4.1 uses a constant chunk size in
    all attempts to determine dimensions, which allows remote attackers to
    cause a denial of service (process or thread consumption) via a large
    TIFF image.

    .. seealso::

     - https://www.cvedetails.com/cve/CVE-2012-3444/
     - https://www.djangoproject.com/weblog/2012/jul/
        30/security-releases-issued/
     - https://github.com/django/django/commit/
        9ca0ff6268eeff92d0d0ac2c315d4b6a8e229155

    .. versionadded:: X.X.X

    """
    desc = "Use of get_image_dimensions affected by CVE-2012-3444."
    funct = context.call_function_name_qual
    if funct == 'django.core.files.images.get_image_dimensions':
        return bandit.Issue(
            severity=bandit.MEDIUM,
            confidence=bandit.LOW,
            text=desc
        )


@test.checks('Call')
@test.test_id('CVE-2013-0306')
def formset_factory_used(context):
    """**CVE-2013-0306: Test for the use of formset_factory**

    The form library in Django 1.3.x before 1.3.6, 1.4.x before 1.4.4, and 1.5
    before release candidate 2 allows remote attackers to bypass intended
    resource limits for formsets and cause a denial of service (memory
    consumption) or trigger server errors via a modified max_num parameter.

    .. seealso::

     - https://www.cvedetails.com/cve/CVE-2013-0306/
     - https://www.djangoproject.com/weblog/2013/feb/19/security/
     - https://github.com/django/django/commit/
        d7094bbce8cb838f3b40f504f198c098ff1cf727
     - https://github.com/django/django/commit/
        0cc350a896f70ace18280410eb616a9197d862b0

    .. versionadded:: X.X.X

    """
    description = "Use of formset_factory affected by CVE-2013-0306."
    if context.is_module_imported_like('django.forms'):
        if context.call_function_name == 'formset_factory':
            return bandit.Issue(
                severity=bandit.MEDIUM,
                confidence=bandit.LOW,
                text=description
            )


@test.checks('Call')
@test.test_id('CVE-2014-0474')
def typecasting_attack(context):
    """**CVE-2014-0474**

    The (1) FilePathField, (2) GenericIPAddressField, and (3) IPAddressField
    model field classes in Django before 1.4.11, 1.5.x before 1.5.6, 1.6.x
    before 1.6.3, and 1.7.x before 1.7 beta 2 do not properly perform type
    conversion, which allows remote attackers to have unspecified impact and
    vectors, related to "MySQL typecasting."

    .. seealso::

     - https://www.cvedetails.com/cve/CVE-2014-0474/
     - https://www.djangoproject.com/weblog/2014/apr/21/security/
     - https://github.com/django/django/commit/
        aa80f498de6d687e613860933ac58433ab71ea4b

    .. versionadded:: X.X.X

    """
    description = "Possible MySQL typecasting check CVE-2014-0474."
    # Include django.db.model and django.db.model.fields
    affected_classes = [
        'FilePathField',
        'GenericIPAddressField',
        'IPAddressField',
    ]
    if context.is_module_imported_like('django.db.model'):
        if context.call_function_name in affected_classes:
            return bandit.Issue(
                severity=bandit.HIGH,
                confidence=bandit.HIGH,
                text=description
            )


@test.checks('Call')
@test.test_id('CVE-DJ-001')
def is_safe_url_used(context):
    r"""**CVE-DJ-001: Test for the use of is_safe_url**

    Related to CVE-2013-6044, CVE-2014-3730, CVE-2015-0220, CVE-2015-2317

    The is_safe_url function in utils/http.py in Django 1.4.x before 1.4.6,
    1.5.x before 1.5.2, and 1.6 before beta 2 treats a URL's scheme as safe
    even if it is not HTTP or HTTPS, which might introduce cross-site
    scripting (XSS) or other vulnerabilities into Django applications that
    use this function, as demonstrated by "the login view in
    django.contrib.auth.views" and the javascript: scheme.

    The django.util.http.is_safe_url function in Django 1.4 before 1.4.13, 1.5
    before 1.5.8, 1.6 before 1.6.5, and 1.7 before 1.7b4 does not properly
    validate URLs, which allows remote attackers to conduct open redirect
    attacks via a malformed URL, as demonstrated by
    "http:\\\djangoproject.com."

    The django.util.http.is_safe_url function in Django before 1.4.18, 1.6.x
    before 1.6.10, and 1.7.x before 1.7.3 does not properly handle leading
    whitespaces, which allows remote attackers to conduct cross-site scripting
    (XSS) attacks via a crafted URL, related to redirect URLs, as demonstrated
    by a "\njavascript:" URL.

    The utils.http.is_safe_url function in Django before 1.4.20, 1.5.x, 1.6.x
    before 1.6.11, 1.7.x before 1.7.7, and 1.8.x before 1.8c1 does not
    properly validate URLs, which allows remote attackers to conduct
    cross-site scripting (XSS) attacks via a control character in a URL,
    as demonstrated by a \x08javascript: URL.

    .. seealso::

     - https://www.cvedetails.com/cve/CVE-2013-6044/
     - https://www.cvedetails.com/cve/CVE-2014-3730/
     - https://www.cvedetails.com/cve/CVE-2015-0220/
     - https://www.cvedetails.com/cve/CVE-2015-2317/

     - https://github.com/django/django/commit/
        2342693b31f740a422abf7267c53b4e7bc487c1b
     - https://github.com/django/django/commit/
        ec67af0bd609c412b76eaa4cc89968a2a8e5ad6a
     - https://github.com/django/django/commit/
        7feb54bbae3f637ab3c4dd4831d4385964f574df
     - https://github.com/django/django/commit/
        4c241f1b710da6419d9dca160e80b23b82db7758

    .. versionadded:: X.X.X

    """
    desc = "Use of is_safe_url affected by" \
           " CVE-2013-6044, CVE-2014-3730, CVE-2015-0220, CVE-2015-2317."

    affected_functions = [
        'django.utils.http.is_safe_url',
        'django.contrib.comments.views.utils.is_safe_url',
        'django.contrib.auth.views.is_safe_url',
        'django.views.i18n.is_safe_url',
    ]
    # Detect also possible bypass
    if context.call_function_name_qual in affected_functions:
        return bandit.Issue(
            severity=bandit.MEDIUM,
            confidence=bandit.MEDIUM,
            text=desc
        )


@test.checks('Call')
@test.test_id('CVE-2015-0222')
def multiplechoice_with_hidden_used(context):
    """**CVE-2015-0222: Test for the use of ModelMultipleChoiceField**

    ModelMultipleChoiceField in Django 1.6.x before 1.6.10 and 1.7.x
    before 1.7.3, when show_hidden_initial is set to True, allows remote
    attackers to cause a denial of service by submitting duplicate values,
    which triggers a large number of SQL queries.

    .. seealso::

     - https://www.cvedetails.com/cve/CVE-2015-0222/
     - https://www.djangoproject.com/weblog/2015/jan/13/security/
     - https://github.com/django/django/commit/
        d7a06ee7e571b6dad07c0f5b519b1db02e2a476c

    .. versionadded:: X.X.X

    """
    desc = "Use of ModelMultipleChoiceField with show_hidden_initial" \
           " affected by CVE-2015-0222."
    if context.is_module_imported_like('django.forms'):
        if context.call_function_name == 'ModelMultipleChoiceField':
            if 'show_hidden_initial' in context.call_keywords:
                if context.call_keywords['show_hidden_initial']:
                    return bandit.Issue(
                        severity=bandit.MEDIUM,
                        confidence=bandit.LOW,
                        text=desc
                    )


@test.checks('Call')
@test.test_id('CVE-2015-2316')
def strip_tags_used(context):
    """**CVE-2015-2316: Test for the use of strip_tags**

    This plugin test checks for the use of the django.utils.html.strip_tags
    function in Django 1.6.x before 1.6.11, 1.7.x before 1.7.7, and 1.8.x
    before 1.8c1, when using certain versions of Python, allows remote
    attackers to cause a denial of service (infinite loop) by increasing
    the length of the input string.

    :Example:

    .. code-block:: none

        >> Issue: Use of django.utils.html.strip_tags detected.
           Severity: Medium   Confidence: Low
        1 strip_tags("do evil")

    .. seealso::

     - https://www.cvedetails.com/cve/CVE-2015-2316/
     - https://www.djangoproject.com/weblog/2015/mar/18/security-releases/
     - https://github.com/django/django/commit/
        b6b3cb9899214a23ebb0f4ebf0e0b300b0ee524f
     - https://github.com/django/django/commit/
        e63363f8e075fa8d66326ad6a1cc3391cc95cd97

    .. versionadded:: X.X.X

    """
    description = "Use of strip_tags affected by CVE-2015-2316."
    affected_functions = [
        'django.utils.html.strip_tags',
        'django.template.defaultfilters.strip_tags'
    ]
    if context.call_function_name_qual in affected_functions:
        return bandit.Issue(
            severity=bandit.MEDIUM,
            confidence=bandit.LOW,
            text=description
        )


@test.checks('Call')
@test.test_id('CVE-2015-8213')
def get_format_used(context):
    """**CVE-2015-8213: Test for the use of get_format**

    The get_format function in utils/formats.py in Django before 1.7.x before
    1.7.11, 1.8.x before 1.8.7, and 1.9.x before 1.9rc2 might allow remote
    attackers to obtain sensitive application secrets via a settings key in
    place of a date/time format setting, as demonstrated by SECRET_KEY.

    .. seealso::

     - https://www.cvedetails.com/cve/CVE-2015-8213/
     - https://www.djangoproject.com/weblog/2015/nov/
        24/security-releases-issued/
     - https://github.com/django/django/commit/
        316bc3fc9437c5960c24baceb93c73f1939711e4

    .. versionadded:: X.X.X

    """
    description = "Use of get_format affected by CVE-2015-8213."
    affected_functions = [
        'django.utils.formats.get_format',
        'django.views.i18n.get_format',
        'django.forms.extras.widgets.get_format'
    ]
    if context.call_function_name_qual in affected_functions:
        if context.node.args:
            format_type = context.node.args[0]
            if not isinstance(format_type, ast.Str):
                return bandit.Issue(
                    severity=bandit.MEDIUM,
                    confidence=bandit.HIGH,
                    text=description
                )
            elif format_type.s not in FORMAT_SETTINGS:
                return bandit.Issue(
                    severity=bandit.MEDIUM,
                    confidence=bandit.HIGH,
                    text=description
                )
