#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import pytest
from unittestzero import Assert

from pages.base_test import BaseTest
from pages.manage_cases_page import MozTrapManageCasesPage


class TestManageCasesPage(BaseTest):

    @pytest.mark.moztrap([142, 137])
    def test_that_user_can_create_and_delete_case(self, mozwebqa_logged_in, product):
        manage_cases_pg = MozTrapManageCasesPage(mozwebqa_logged_in)

        case = self.create_case(mozwebqa_logged_in, product, use_API=False)

        manage_cases_pg.filter_form.filter_by(lookup='name', value=case['name'])

        Assert.true(manage_cases_pg.is_element_present(*case['locator']))

        manage_cases_pg.delete_case(name=case['name'])

        Assert.false(manage_cases_pg.is_element_present(*case['locator']))

    def test_that_deleting_single_version_of_case_does_not_delete_all_versions(self, mozwebqa_logged_in, product):
        """test for https://www.pivotaltracker.com/projects/280483#!/stories/40857085"""

        #prerequisites
        first_version = product['version']
        test_case = self.create_case(mozwebqa_logged_in, product=product, use_API=True, version=first_version)
        second_version = self.create_version(mozwebqa_logged_in, product=product)
        product_versions = [u'%s %s' % (product['name'], version['name']) for version in (first_version, second_version)]

        manage_cases_pg = MozTrapManageCasesPage(mozwebqa_logged_in)
        manage_cases_pg.go_to_manage_cases_page()
        filter_item = manage_cases_pg.filter_form.filter_by(lookup='product', value=product['name'])
        test_cases = manage_cases_pg.test_cases

        #remember case version and delete case
        deleted_version = test_cases[0].product_version
        product_versions.remove(deleted_version)
        test_cases[0].delete()

        filter_item.remove_filter()
        manage_cases_pg.filter_form.filter_by(lookup='name', value=test_case['name'])
        test_cases = manage_cases_pg.test_cases

        #check that there is only one test case left and ensure its version equals to second version
        Assert.equal(len(test_cases), 1, u'there should be only one case')
        Assert.equal(test_cases[0].name, test_case['name'], u'that\'s wrong test case')
        Assert.equal(test_cases[0].product_version, product_versions[0], u'that\'s wrong product version')

    def test_that_manage_cases_list_shows_all_case_versions_individually(self, mozwebqa_logged_in, product):
        """https://www.pivotaltracker.com/projects/280483#!/stories/40857159"""

        #prerequisites
        first_version = product['version']
        test_case = self.create_case(mozwebqa_logged_in, product=product, use_API=True, version=first_version)
        second_version = self.create_version(mozwebqa_logged_in, product=product)
        product_versions = [u'%s %s' % (product['name'], version['name']) for version in (first_version, second_version)]

        manage_cases_pg = MozTrapManageCasesPage(mozwebqa_logged_in)
        manage_cases_pg.go_to_manage_cases_page()
        manage_cases_pg.filter_form.filter_by(lookup='name', value=test_case['name'])
        filtered_cases = manage_cases_pg.test_cases

        for case in filtered_cases:
            Assert.equal(case.name, test_case['name'], u'that\'s wrong case we\'ve got here')

        #check that both product versions are displayed
        Assert.equal(
            sorted(product_versions),
            sorted([case.product_version for case in filtered_cases]),
            u'expected product versions of test cases don\'t match actual ones')
