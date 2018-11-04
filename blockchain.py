import hashlib
import json
from time import time
from uuid import uuid4


class Blockchain(object):
    def __init__(self):
        self.current_transactions = []
        self.chain = []

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

        self.chain_append(block)
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
