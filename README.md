# bytom-utils

### merge_utxo.py

```
usage: merge_utxo.py [-h] [-o ENDPOINT] [--http-user HTTP_USER]
                     [--http-pass HTTP_PASS] [--cert HTTPS_CERT]
                     [--key HTTPS_KEY] [--ca HTTPS_CA] [--no-verify]
                     [-p BYTOM_PASS] [-l] [-m MERGE_LIST] [-a ADDRESS] [-y]

Bytom UTXO Tool

optional arguments:
  -h, --help            show this help message and exit
  -o ENDPOINT, --url ENDPOINT
                        API endpoint
  --http-user HTTP_USER
                        HTTP Basic Auth Username
  --http-pass HTTP_PASS
                        HTTP Basic Auth Password
  --cert HTTPS_CERT     HTTPS Client Certificate
  --key HTTPS_KEY       HTTPS Client Key
  --ca HTTPS_CA         HTTPS CA Certificate
  --no-verify           Do not verify HTTPS server certificate
  -p BYTOM_PASS, --pass BYTOM_PASS
                        Bytom Account Password
  -l, --list            Show UTXO list without merge
  -m MERGE_LIST, --merge MERGE_LIST
                        UTXO to merge
  -a ADDRESS, --address ADDRESS
                        Transfer address
  -y, --yes             Confirm transfer
```

Connect To Localhost

```
python3 merge_utxo.py -l
```

Connect To HTTPS Host

```
python3 merge_utxo.py -o https://btm:8443 --cert=client.pem --key=client.key --ca=ca.pem -l
python3 merge_utxo.py -o https://btm:8443 --cert=client.pem --key=client.key --ca=ca.pem -m 1,3,5 -y -a bm1aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa -p yourpasswordhere
```

Interactive

```
python3 merge_utxo.py -o https://btm:8443 --cert=client.pem --key=client.key --ca=ca.pem
   0.  412.50000000 BTM xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   1.  412.50000000 BTM xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx (not mature)
   2.  300.00000000 BTM xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   3.  412.50000000 BTM xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx (not mature)
   4.  412.50000000 BTM xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   5.  412.50000000 BTM xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx (not mature)
   6.  412.50000000 BTM xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx (not mature)
Merge UTXOs (1,3,5 or 1-10 or all): 0,2-5
Ignored: UTXO[3] not mature
Ignored: UTXO[5] not mature
To merge 3 UTXOs with 1125.00000000 BTM
Transfer Address: bm1aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
Bytom Account Password: (password not echo)
Confirm [y/N] y
ffeeddccbbaa99887766554433221100ffeeddccbbaa99887766554433221100
```