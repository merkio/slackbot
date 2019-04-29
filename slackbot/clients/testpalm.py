import requests
import logging


# -*- coding: utf-8 -*-

import json
import random
import requests
import constants
import tagger


def build_eq_filter_object(arg, key):

    """

    :param arg:
    :param key:
    :return:
    """
    value = arg.pop(0)
    return {
        'type': 'EQ',
        'key': key,
        'value': value
    }

# можно зашить ключ в объект коллекции (кейсы/фичи) и тогда его можно будет
# не предавать явно
def build_filter_endpoint(arg, key):
    return {
        'type': 'OR',
        'left': build_eq_filter_object(arg, key),
        'right': build_eq_filter_object(arg, key)
    }


def add_is_autotest_key(filter_=None, value=None):
    assert value in (True, False)
    if filter_:
        return {
            'type': 'AND',
            'left': filter_,
            'right': {
                'type': 'EQ',
                'key': 'isAutotest',
                'value': value
            }
        }
    else:
        raise RuntimeError('code is still used!') # delete branch if no
        # exceptions occured
        # return {
        #     'type': 'EQ',
        #     'key': 'isAutotest',
        #     'value': value
        # }


def add_status_key(filter_, value):
    assert value in ('actual',)
    return {
        'type': 'AND',
        'left': filter_,
        'right': {
            'type': 'EQ',
            'key': 'status',
            'value': value
        }
    }


def add_checklist_key(value):
    assert value in ('Smoke',)
    return {
        'type': 'EQ',
        'key': constants.CHECK_LIST_KEY_ID,
        'value': value
    }


def build_suite_filter(type_, key, cases=None):
    result = None

    if type_ == 'manual' and not cases:
        raise ValueError(f'"cases" parameter cannot be {cases} in '
                         'manual run filter')
    if type_ == 'manual':
        result = build_filter_endpoint(cases, key)
        cases_copy = cases[:]
        for _ in cases_copy:
            result = {
                'type': 'OR',
                'left': result,
                'right': build_eq_filter_object(cases, key)
            }
        result = add_is_autotest_key(result, False)
    elif type_ == 'auto':
        result = add_is_autotest_key(result, True)
    else:
        raise ValueError(f'unrecognized "type_" arg - "{type_}"\npass only '
                         f'"manual" "auto" or "counting"')
    result = add_status_key(result, 'actual')
    result = exclude_partners(result)
    return result


def find_temporary_suite():
    suites = requests.get(f'{constants.TESTPALM_TESTSUITE_URL}',
                          headers=constants.OAUTH_HEADER)
    for suite in suites.json():
        if suite['title'] == 'test':
            return suite['id']
    return None


def del_temporary_suite(temp_suite_id):
    resp = requests.delete(f'{constants.TESTPALM_TESTSUITE_URL}{temp_suite_id}',
                           headers=constants.OAUTH_HEADER)
    if resp.status_code == 200 and not resp.text:
        print(f'temporary suite successfully deleted')
    else:
        message = f'error while deleting temporary suite\n'
        message = f'{resp.status_code}\n'
        message += resp.text
        raise RuntimeError(message)


def create_suite(filter_):
    filter_expression = {
        'filter': {
            'expression': filter_
        },
        'title': 'test',
    }
    temp_suite_id = find_temporary_suite()
    if temp_suite_id:
        del_temporary_suite(temp_suite_id)
    filter_expression = json.dumps(filter_expression, ensure_ascii=False)
    resp = requests.post(constants.TESTPALM_TESTSUITE_URL,
                         data=filter_expression,
                         headers=constants.TESTPALM_CONTENT_HEADERS)
    try:
        return resp.json()['id']
    except KeyError:
        message = f'error while creating suite\n{resp.json()}'
        raise RuntimeError(message)


def create_run(version, suite_id, tester=None):
    if tester:
        title = f'{version} - {tester}'
    else:
        title = f'[AUTO] {version}'
    payload = {
        'title': f'{title}',
        'internalResolveAllowed': 'true',
        'version': version,
        'environments': [{                    # FOR ASESSORS
            'title': 'Android Smart >= 4.4'   # FOR ASESSORS
        }],
        'currentEnvironment' : {
            'title': 'Android Smart >= 4.4'
        }
    }
    raw_payload = json.dumps(payload, ensure_ascii=False, separators=(",", ": "))
    raw_payload = raw_payload.encode('utf-8')
    resp = requests.post(
        f'{constants.TESTPALM_TESTRUN_URL}{suite_id}',
        data=raw_payload,
        headers=constants.TESTPALM_CONTENT_HEADERS,
    )
    # while resp.json() and resp.json()['data']['code'] == 500:
    #         time.sleep(5)
    #         print('were in loop')
    #         resp = requests.post(
    #             f'{constants.TESTPALM_TESTRUN_URL}{suite_id}',
    #             data=raw_payload,
    #             headers=constants.TESTPALM_CONTENT_HEADERS,
    #         )
    #         print('#new resp', resp.text)

    if resp.status_code == 200:
        print(f'run "{title}" successfully created')
        return resp.text
    else:
        raise RuntimeError('Error while creating run:\n', resp.text)


def create_auto_run(version):
    print('creating auto run...')
    filter_ = build_suite_filter('auto', None)
    suite_id = create_suite(filter_)
    create_run(version, suite_id)


# hack. refactor
def exclude_partners(result):
    return {
        'type': 'AND',
        'left': result,
        'right': {
            'type': 'NOT',
            'left': {
                "type": "OR",
                "left": {
                    "type": "OR",
                    "left": {
                        "type": "EQ",
                        "key": constants.PARTNERS_KEY_ID,
                        "value": "ZenApp"
                    },
                    "right": {
                        "type": "EQ",
                        "key": constants.PARTNERS_KEY_ID,
                        "value": "Y.Browser"
                    }
                },
                "right": {
                    "type": "EQ",
                    "key": constants.PARTNERS_KEY_ID,
                    "value": "Y.Launcher"
                }
            }
        }
    }


def get_smoke_cases():
    filter_ = add_checklist_key('Smoke')
    filter_ = add_is_autotest_key(filter_, False)
    filter_ = add_status_key(filter_, 'actual')
    filter_ = exclude_partners(filter_)
    filter_ = json.dumps(filter_, ensure_ascii=False, separators=(",", ": "))
    print('filter_', filter_)
    resp = requests.get(constants.TESTPALM_TESTCASES_URL,
                        params={'expression': filter_},
                        headers=constants.OAUTH_HEADER)
    return [c['id'] for c in resp.json()]


def get_all_cases(version):
    """Return list of IDs of testcases for given version"""

    features = tagger.get_tp_features(version)
    filter_ = build_suite_filter('manual', constants.FEATURE_KEY_ID, features)
    filter_ = json.dumps(filter_, ensure_ascii=False, separators=(",", ": "))
    resp = requests.get(constants.TESTPALM_TESTCASES_URL,
                        params={'expression': filter_},
                        headers=constants.OAUTH_HEADER)
    return [c['id'] for c in resp.json()]


def divide(all_cases, testers):
    """Split given testcases """

    assert isinstance(all_cases, list)
    assert isinstance(testers, list)
    *firsts, last = testers
    result = {}
    cases_count = len(all_cases) // len(testers)
    for tester in firsts:
        cases = random.sample(all_cases, cases_count)
        for case in cases:
            all_cases.remove(case)
        result[tester] = cases
    result[last] = all_cases
    return result


def create_manual_runs(testers, version):
    print('creating manual runs...')
    # todo remove shuffle since we random pick case
    random.shuffle(testers)
    all_cases = get_all_cases(version)
    # todo do we need to add smoke cases since we automate them?
    x = get_smoke_cases()
    all_cases.extend(x)
    # todo do we need a list?
    all_cases = list(set(all_cases))
    cases_for_tester = divide(all_cases, testers)
    runs = {}
    for tester in testers:
        filter_ = build_suite_filter('manual', 'id', cases_for_tester[tester])
        suite_id = create_suite(filter_)
        run_id = create_run(version, suite_id, tester)
        runs[tester] = run_id
    return runs
