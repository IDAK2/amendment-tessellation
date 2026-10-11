import json
import re
import time
from pathlib import Path

from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet
from genlayer_py.contracts import actions as contract_actions


def calldata_compat(method=None, args=None, kwargs=None):
    result = {}
    if method is not None:
        result['method'] = method
    if args:
        result['args'] = args
    if kwargs:
        result['kwargs'] = kwargs
    return result


contract_actions.make_calldata_object = calldata_compat
ROOT = Path(__file__).parents[1]
ENV = (ROOT.parents[3] / 'accounts.env').read_text()
DEPLOYMENT = json.loads((ROOT / 'deployment.json').read_text())
ADDRESS = DEPLOYMENT['contractAddress']
COMMIT = DEPLOYMENT['sourceCommit']


def account(number):
    key = re.search(rf'^ACCOUNT_{number}_GENLAYER_PRIVATE_KEY\\s*=\\s*"?([^"\\r\\n]+)', ENV, re.M).group(1).strip()
    return create_account(account_private_key=key)


def client(number):
    return create_client(chain=studionet, account=account(number))


def write(number, name, args):
    active = client(number)
    tx = active.write_contract(address=ADDRESS, function_name=name, args=args)
    print(name + '_tx=' + str(tx), flush=True)
    receipt = active.wait_for_transaction_receipt(transaction_hash=tx, wait_until='finalized', retries=180, interval=5000, full_transaction=True)
    leaders = receipt.get('consensus_data', {}).get('leader_receipt') or []
    leaders = [leaders] if isinstance(leaders, dict) else leaders
    assert receipt.get('result_name') == 'MAJORITY_AGREE'
    assert any(item.get('execution_result') == 'SUCCESS' for item in leaders)
    return str(tx)

tessellation_id = 'TILE-' + str(int(time.time()))
role_numbers = (1, 3, 4)
proposers = [str(account(number).address) for number in role_numbers]
transactions = {}
transactions['open'] = write(7, 'open_tessellation', [
    tessellation_id, 'Neighborhood assembly access motion',
    'Provide dependable access services for every monthly neighborhood assembly.',
    'Amendments must govern meeting access, rooms, notices, childcare, or remote participation.',
    proposers, 3600,
])
amendments = [
    'Reserve the east room for evening childcare during every scheduled assembly.',
    'Use the east room exclusively for equipment storage during evening assemblies.',
    'Publish an accessibility contact and remote participation link with every agenda.',
]
for number, amendment in zip(role_numbers, amendments):
    transactions['amendment' + str(number)] = write(number, 'submit_amendment', [tessellation_id, amendment])
transactions['compose'] = write(7, 'compose', [tessellation_id])
state = client(7).read_contract(address=ADDRESS, function_name='get_tessellation', args=[tessellation_id])
assert state['state'] == 'PACKAGE'
assert state['conflict_pairs'] == [[0, 1]]
assert state['package_indexes'] == [0, 2]
proof = {'tessellationId': tessellation_id, 'transactions': transactions, 'state': state,
         'disclosure': 'The proposer wallets are operator-controlled role fixtures, not independent legislators.'}
(ROOT / 'evidence').mkdir(exist_ok=True)
(ROOT / 'evidence' / 'live-proof.json').write_text(json.dumps(proof, indent=2) + '\n')
print(json.dumps(proof, indent=2), flush=True)

