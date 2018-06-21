import json, time, argparse, getpass, re, requests

try:
   input = raw_input
except NameError:
   pass

parser = argparse.ArgumentParser(description='Bytom UTXO Tool')
parser.add_argument('-o', '--url', default='http://127.0.0.1:9888', dest='endpoint', help='API endpoint')
parser.add_argument('--http-user', default=None, dest='http_user', help='HTTP Basic Auth Username')
parser.add_argument('--http-pass', default=None, dest='http_pass', help='HTTP Basic Auth Password')
parser.add_argument('--cert', default=None, dest='https_cert', help='HTTPS Client Certificate')
parser.add_argument('--key', default=None, dest='https_key', help='HTTPS Client Key')
parser.add_argument('--ca', default=None, dest='https_ca', help='HTTPS CA Certificate')
parser.add_argument('--no-verify', action='store_true', dest='https_verify', help='Do not verify HTTPS server certificate')
parser.add_argument('-p', '--pass', default=None, dest='bytom_pass', help='Bytom Account Password')
parser.add_argument('-l', '--list', action='store_true', dest='only_list', help='Show UTXO list without merge')
parser.add_argument('-m', '--merge', default=None, dest='merge_list', help='UTXO to merge')
parser.add_argument('-a', '--address', default=None, dest='address', help='Transfer address')
parser.add_argument('-y', '--yes', action='store_true', dest='confirm', help='Confirm transfer')

class BytomException(Exception):
    pass

class JSONRPCException(Exception):
    pass

class Callable(object):
    def __init__(self, name, func):
        self.name = name
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(self.name, *args, **kwargs)

class JSONRPC(object):
    def __init__(self, endpoint, httpverb='POST', **kwargs):
        self.url = endpoint.rstrip('/')
        self.httpverb = httpverb
        self.kwargs = kwargs

    def __getattr__(self, name):
        return Callable(name.replace('_', '-'), self.callMethod)

    def callMethod(self, method, params={}):
        m = requests.request(self.httpverb, '{}/{}'.format(self.url, method), json=params, **self.kwargs)
        data = m.json()
        if data.get('status') == 'success':
            return data['data']
        raise JSONRPCException(data.get('msg') or data.get('message') or str(data))

def send_tx(bytomd, utxo_list, to_address, password):
    actions = []
    amount = 0
    for utxo in utxo_list:
        actions.append({
            'type': 'spend_account_unspent_output',
            'output_id': utxo['id'],
        })
        amount += utxo['amount']

    actions.append({
        'amount': amount,
        'asset_id': 'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff',
        'type': 'control_address',
        'address': to_address,
    })

    transaction = bytomd.build_transaction({
        'base_transaction' : None,
        'actions' : actions,
        'ttl' : 1
    })

    gas_info = bytomd.estimate_transaction_gas({
        'transaction_template': transaction
    })
    fee = gas_info['total_neu']
    actions[-1]['amount'] -= fee

    time.sleep(1)

    transaction = bytomd.build_transaction({
        'base_transaction': None,
        'actions': actions,
        'ttl': 1,
    })

    signed_transaction = bytomd.sign_transaction({
        'transaction': transaction,
        'password': password,
    })

    if signed_transaction['sign_complete']:
        raw_transaction = signed_transaction['transaction']['raw_transaction']
        result = bytomd.submit_transaction({'raw_transaction': raw_transaction})
        return result['tx_id']
    else:
        raise BytomException('Sign not complete')

def parse_id_list(id_list_str, list_all):
    for id_str in id_list_str.split(','):
        id_ = id_str.strip()

        if not id_:
            pass
        elif id_.strip().lower() == 'all':
            for i in list_all:
                yield i
            return
        elif re.match('(\d+)-(\d+)', id_):
            start, end = re.match('(\d+)-(\d+)', id_).groups()
            for i in range(int(start), int(end) + 1):
                yield i
        elif not id_.strip().isdigit():
            print('Ignored: Incorrect index {}'.format(id_))
        else:
            idx = int(id_.strip())
            yield idx

def main():
    options = parser.parse_args()
    api_params = {}
    if options.http_user and options.http_pass:
        api_params['auth'] = (options.http_user, options.http_pass)
    if options.https_cert:
        if options.https_key:
            api_params['cert'] = (options.https_cert, options.https_key)
        else:
            api_params['cert'] = options.https_cert

    if options.https_ca:
        api_params['verify'] = options.https_ca
    elif options.https_verify:
        api_params['verify'] = False

    bytomd = JSONRPC(options.endpoint, **api_params)
    utxolist = bytomd.list_unspent_outputs()
    current_block = bytomd.get_block_count()['block_count']
    for i, utxo in enumerate(utxolist):
        print('{:4}. {:13.8f} BTM {}{}'.format(i, utxo['amount'] / 1e8, utxo['id'], ' (not mature)' if utxo['valid_height'] > current_block else ''))

    if options.only_list:
        return

    utxo_idlist = options.merge_list or input('Merge UTXOs (1,3,5 or 1-10 or all): ')
    utxo_mergelist = []
    utxo_idset = set()
    for idx in parse_id_list(utxo_idlist, range(len(utxolist))):
        if idx in utxo_idset:
            print('Ignored: Duplicate index {}'.format(idx))
        elif not 0 <= idx < len(utxolist):
            print('Ignored: Index out of range {}'.format(idx))
        elif utxolist[idx]['valid_height'] > current_block:
            print('Ignored: UTXO[{}] not mature'.format(idx))
        else:
            utxo_mergelist.append(utxolist[idx])
            utxo_idset.add(idx)

    if len(utxo_mergelist) < 2:
        print('Not Merge UTXOs, Exit...')
        return

    print('To merge {} UTXOs with {:13.8f} BTM'.format(len(utxo_mergelist), sum(utxo['amount'] for utxo in utxo_mergelist) / 1e8))

    if not options.address:
        options.address = input('Transfer Address: ')

    if not options.bytom_pass:
        options.bytom_pass = getpass.getpass('Bytom Account Password: ')

    if not (options.confirm or input('Confirm [y/N] ').lower() == 'y'):
        print('Not Merge UTXOs, Exit...')
        return

    print(send_tx(bytomd, utxo_mergelist, options.address, options.bytom_pass))

if __name__ == '__main__':
    main()
