import time
import requests
import json
import argparse
from models import Block, Txn



def get_parser_args():
    pass

class Syncer(object):
    def __init__(self, from_num=0, reverse=False):
        self.from_num = from_num
        self.reverse = reverse
        self.cur_num = from_num
        self.api_url = "https://api.myetherapi.com/eth"

    def run(self):
        while True:
            if self.is_synced(self.cur_num):
                self.update_cur_num()
            else:
                if self.sync_block(self.cur_num):
                    self.update_cur_num()
            if self.reverse:
                continue
            if self.is_genesis_block():
                return
            time.sleep(13)


    def update_cur_num(self):
        if self.reverse:
            tmp_num = hex_to_int(self.cur_num) - 1
        else:
            tmp_num = hex_to_int(self.cur_num) + 1
        self.cur_num = int_to_hex(tmp_num)

    def is_synced(self, num):
        try:
            Block.get(Block.number == num)
            return True
        except Exception:
            return False

    def sync_block(self, block_num):
        latest_num = self.get_latest_block_num()
        if hex_to_int(block_num) > hex_to_int(latest_num):
            return False
        block_info, is_ok = self.get_block_from_rpc(block_num)
        if is_ok:
            return self.save_to_db(block_info)
        return False

    def get_latest_block_num(self):
        payload = get_payload("eth_blockNumber",[])
        return self.rpc(self.api_url, payload)

    def get_block_from_rpc(self, block_num):
        payload = gen_payload("eth_getBlockByNumber",[block_num, True])
        return self.rpc(self.api_url, payload)

    def rpc(self, api_url, payload):
        headers = {"content-type": "application/json"}
        resp = requests.post(api_url, data=payload, headers=headers).json()
        #TODO: check id
        if resp['error']:
            return resp['error'], False
        return resp['result'], True


    def save_to_db(self, block_info):
        block = Block.create(
            number=block_info['number'],
            blockhash=block_info['hash'],
            parenthash=block_info['parentHash'],
            miner=block_info['miner'],
            logs_bloom=block_info['logsBloom'],
            timestamp=block_info['timestamp'])
        for item in block_info['transactions']:
            Txn.create()


def gen_payload(method, params):
    payload ={
        "method": method,
        "jsonrpc": "2.0",
        "params": params,
        "id": gen_id()
    }
    return json.dumps(payload)


def is_genesis_block(block_num):
    return hex_to_int(block_num) == 0

def hex_to_int(hex_num):
    return int(hex_num, 0)

def int_to_hex(num):
    return hex(num)
        

def main():
    syncer = Syncer(from_num="0x409bdb")
    syncer.run()


if __name__ == "__main__":
    main()
