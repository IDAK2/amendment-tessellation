from conftest import CONTRACT
import json


TEXTS = [
    'Reserve the east room for evening childcare during every scheduled assembly.',
    'Use the east room exclusively for equipment storage during evening assemblies.',
    'Publish an accessibility contact and remote participation link with every agenda.',
]


def opened(vm, deploy, accounts, window=600, proposer_count=3):
    vm.strict_mocks = True
    vm.check_pickling = True
    vm.warp('2035-01-01T00:00:00+00:00')
    vm.sender = accounts[0]
    contract = deploy(CONTRACT)
    contract.open_tessellation(
        'tile-6', 'Neighborhood assembly access motion',
        'Provide dependable access services for every monthly neighborhood assembly.',
        'Amendments must govern meeting access, rooms, notices, childcare, or remote participation.',
        ['0x' + a.hex() for a in accounts[1:proposer_count + 1]], window,
    )
    return contract


def submit(vm, contract, accounts, indexes=(1, 2, 3)):
    for account_index, text in zip(indexes, TEXTS):
        vm.sender = accounts[account_index]
        contract.submit_amendment('tile-6', text)


def llm(vm, pairs=None, statuses=None):
    pairs = [[0, 1]] if pairs is None else pairs
    statuses = statuses or ['IN_SCOPE'] * 3
    vm.mock_llm(r'.*AmendmentTessellation conflict mapping.*', json.dumps({
        'statuses': [{'index': i, 'status': value} for i, value in enumerate(statuses)],
        'conflict_pairs': pairs,
    }))


def test_maximum_compatible_package(direct_vm, direct_deploy, direct_accounts):
    contract = opened(direct_vm, direct_deploy, direct_accounts)
    submit(direct_vm, contract, direct_accounts); llm(direct_vm)
    contract.compose('tile-6')
    row = contract.get_tessellation('tile-6')
    assert row['state'] == 'PACKAGE'
    assert row['package_indexes'] == [0, 2]
    assert row['conflict_pairs'] == [[0, 1]]


def test_out_of_scope_amendment_excluded(direct_vm, direct_deploy, direct_accounts):
    contract = opened(direct_vm, direct_deploy, direct_accounts)
    submit(direct_vm, contract, direct_accounts); llm(direct_vm, [], ['IN_SCOPE', 'OUT_OF_SCOPE', 'IN_SCOPE'])
    contract.compose('tile-6')
    assert contract.get_tessellation('tile-6')['package_indexes'] == [0, 2]


def test_named_proposer_and_replay(direct_vm, direct_deploy, direct_accounts):
    contract = opened(direct_vm, direct_deploy, direct_accounts)
    direct_vm.sender = direct_accounts[4]
    with direct_vm.expect_revert('named proposer'):
        contract.submit_amendment('tile-6', TEXTS[0])
    direct_vm.sender = direct_accounts[1]
    contract.submit_amendment('tile-6', TEXTS[0])
    with direct_vm.expect_revert('one amendment'):
        contract.submit_amendment('tile-6', TEXTS[0])


def test_sparse_expired_collection_uses_dense_indexes(direct_vm, direct_deploy, direct_accounts):
    contract = opened(direct_vm, direct_deploy, direct_accounts, 30, 4)
    submit(direct_vm, contract, direct_accounts, (1, 3, 4))
    direct_vm.warp('2035-01-01T00:00:31+00:00'); llm(direct_vm)
    contract.compose('tile-6')
    assert contract.get_tessellation('tile-6')['state'] == 'PACKAGE'


def test_validator_rejects_forged_conflict_graph(direct_vm, direct_deploy, direct_accounts):
    contract = opened(direct_vm, direct_deploy, direct_accounts)
    submit(direct_vm, contract, direct_accounts); llm(direct_vm)
    row = contract.tessellations['TILE-6']
    texts = [{'index': i, 'proposer_index': i, 'text': TEXTS[i]} for i in range(3)]
    result = contract._map(row, texts)
    assert direct_vm.run_validator(leader_result=result) is True
    forged = {'statuses': result['statuses'], 'conflict_pairs': []}
    assert direct_vm.run_validator(leader_result=forged) is False


def test_permissionless_incomplete_close(direct_vm, direct_deploy, direct_accounts):
    contract = opened(direct_vm, direct_deploy, direct_accounts, 30)
    direct_vm.warp('2035-01-01T00:00:31+00:00'); direct_vm.sender = direct_accounts[5]
    contract.close_incomplete('tile-6')
    assert contract.get_tessellation('tile-6')['state'] == 'INCOMPLETE'
