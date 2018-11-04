import hashlib
import json
import requests
from time import time
from urllib.parse import urlparse


class Blockchain(object):
    def __init__(self):
        self.current_transactions = []
        self.chain = []

        self.nodes = set()

        # genesis block 생성
        self.new_block(previous_hash=1, proof=100)

    def proof_of_work(self, last_proof):
        """
        POW 알고리즘 설명:
        - 앞에서 0의 개수가 4개가 나오는 hash(pp')을 만족시키는 p'을 찾는다.
        - p 는 이전 블록의 proof, p' 는 새로운 블록의 proof

        :param last_proof : <int>
        :return : <int>
        """

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Proof 검증 방법 : hash(last_proof, proof)의 값의 앞의 4자리가 0인가?

        :param last_proof : <int> 이전 블록의 proof 값
        :param proof : <int> 현재 블록의 proof 값
        :return : <bool> 옳다면 true 값 그렇지 않으면 false 값 반환
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def new_block(self, proof, previous_hash=None):
        """

        블록체인에 새로운 블록 만들기

        :param proof: <int> proof 는 Proof of Work 알고리즘에 의해서 제공된다.
        :param previous_hash: (Optional) <str> 이전 블록의 해쉬값
        :return : <dict> 새로운 블록

        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.last_block),
        }

        # 거래 내역 초기화
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        다음에 채굴될 블록(새로운 블록)에 들어갈 거래내역

        :param sender : <str> sender의 주소
        :param recipient : <str> recipient의 주소
        :param amount : <int> amount
        :return : <int> 이 거래내역들을 포함하는 블록의 index
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block

        :param block: <dict> Block
        :return : <str>
        """

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def register_node(self, address):
        """
        새로운 노드가 기존의 노드의 list 에 등록되는 곳이다
        'http://172.0.0.1:5002 와 같은 형태로 등록을 요청하면 된다
        """

        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

        def valid_chain(self, chain):
            """
            주어진 블록체인이 유효한지를 결정한다.
            """

            last_block = chain[0]
            current_index = 1

            while current_index < len(chain):
                block = chain[current_index]
                print(f'{last_block}')
                print(f'{block}')
                print("\n-----------\n")

                if block['previous_hash'] != self.hash(last_block):
                    return False

                if not self.valid_proof(last_block['proof'], block['proof']):
                    return False

                last_block = block
                current_index += 1

            return True

    def resolve_conflicts(self):
        """
        이곳이 우리의 합의 알고리즘이다, 노드 중에서 가장 긴 체인을 가지고 있는 노드의 체인을 유효한 것으로 인정한다.
        """

        neighbours = self.nodes
        new_chain = None

        max_length = len(self.chain)

        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False

    def valid_chain(self, chain):
        """
        주어진 블록체인이 유효한지를 결정한다.
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")

            if block['previous_hash'] != self.hash(last_block):
                return False

            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        이곳이 우리의 합의 알고리즘이다, 노드 중에서 가장 긴 체인을 가지고 있는 노드의 체인을 유효한 것으로 인정한다.
        """

        neighbours = self.nodes
        new_chain = None

        max_length = len(self.chain)

        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False
