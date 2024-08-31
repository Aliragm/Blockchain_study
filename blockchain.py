import hashlib
import json
import requests
from urllib.parse import urlparse
from textwrap import dedent
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request

class Blockchain(object):
    def __init__(self):
        # Inicializa a blockchain e uma lista de transações atuais
        self.chain = []  # Lista que irá armazenar a blockchain completa
        self.currentTransactions = []  # Lista de transações que serão incluídas no próximo bloco
        self.nodes = set()  # Conjunto de nós registrados na rede
        # Cria o bloco gênesis (primeiro bloco da blockchain)
        self.newBlock(previousHash=1, proof=100)

    def newBlock(self, proof, previousHash=None):
        """
        Cria um novo bloco na blockchain
        :param proof: <int> O proof (prova) fornecido pelo algoritmo de Proof of Work
        :param previous_hash: (Opcional) <str> Hash do bloco anterior
        :return: <dict> Novo bloco
        """
        block = {
            'index': len(self.chain) + 1,  # Índice do bloco (posição na blockchain)
            'timestamp': time(),  # Timestamp do momento em que o bloco é criado
            'transactions': self.currentTransactions,  # Transações que estão sendo incluídas no bloco
            'proof': proof,  # Prova obtida através do algoritmo de Proof of Work
            'previousHash': previousHash or self.hash(self.chain[-1])  # Hash do bloco anterior ou, no caso do bloco gênesis, um hash inicial
        }

        # Reseta a lista de transações atuais, pois elas já foram incluídas em um bloco
        self.currentTransactions = []

        # Adiciona o novo bloco à blockchain
        self.chain.append(block)
        return block

    def newTransaction(self, sender, recipient, amount):
        """
        Cria uma nova transação para ser incluída no próximo bloco minerado
        :param sender: <str> Endereço do remetente
        :param recipient: <str> Endereço do destinatário
        :param amount: <int> Quantidade
        :return: <int> O índice do bloco que irá conter esta transação
        """
        self.currentTransactions.append({
            'sender': sender,  # Endereço do remetente
            'recipient': recipient,  # Endereço do destinatário
            'amount': amount  # Quantidade transferida
        })

        # Retorna o índice do bloco que irá conter a transação
        return self.lastBlock['index'] + 1

    def proofOfWork(self, lastProof):
        """
        Algoritmo simples de Proof of Work:
         - Encontre um número p' tal que hash(pp') contenha 4 zeros à esquerda, onde p é o proof anterior e p' é o novo proof
        :param last_proof: <int> Prova anterior
        :return: <int> Nova prova
        """

        proof = 0
        # Continua tentando até encontrar um proof válido
        while self.validProof(lastProof, proof) is False:
            proof += 1
        return proof

    def registerNode(self, address):
        """
        Adiciona um novo nó à lista de nós
        :param address: <str> Endereço do nó. Ex.: 'http://192.168.0.5:5000'
        :return: None
        """
        # Analisa a URL e adiciona o nó à lista de nós registrados
        parsedUrl = urlparse(address)
        self.nodes.add(parsedUrl.netloc)
    
    def validChain(self, chain):
        """
        Determina se uma blockchain fornecida é válida
        :param chain: <list> Uma blockchain
        :return: <bool> True se válida, False se não for
        """
        lastBlock = chain[0]
        currentIndex = 1

        # Verifica se cada bloco na cadeia é válido
        while currentIndex < len(chain):
            block = chain[currentIndex]
            print(f'{lastBlock}')
            print(f'{block}')
            print("\n-----------\n")

            # Verifica se o hash do bloco anterior está correto
            if block['previousHash'] != self.hash(lastBlock):
                return False

            # Verifica se o proof do bloco é válido
            if not self.validProof(lastBlock['proof'], block['proof']):
                return False

            lastBlock = block
            currentIndex += 1
        return True
    
    def resolveConflicts(self):
        """
        Este é o nosso Algoritmo de Consenso, ele resolve conflitos
        substituindo nossa cadeia pela mais longa na rede.
        :return: <bool> True se nossa cadeia foi substituída, False se não foi
        """
        neighbours = self.nodes
        newChain = None

        # Apenas considera cadeias mais longas que a nossa
        maxLength = len(self.chain)

        # Verifica todas as cadeias dos nós na rede
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Verifica se a cadeia recebida é mais longa e válida
                if length > maxLength and self.validChain(chain):
                    maxLength = length
                    newChain = chain

        # Substitui a cadeia atual se encontrar uma nova cadeia válida e mais longa
        if newChain:
            self.chain = newChain
            return True

        return False

    @staticmethod
    def validProof(lastProof, proof):
        """
        Valida o Proof: Verifica se o hash(last_proof, proof) contém 4 zeros à esquerda
        :param last_proof: <int> Prova anterior
        :param proof: <int> Prova atual
        :return: <bool> True se correto, False se não for.
        """
        # Concatena as provas e calcula o hash
        guess = f'{lastProof}{proof}'.encode()
        guessHash = hashlib.sha256(guess).hexdigest()
        # Verifica se os 4 primeiros caracteres do hash são zeros
        return guessHash[:4] == "0000"

    @staticmethod
    def hash(block):
        """
        Cria um hash SHA-256 de um bloco
        :param block: <dict> Bloco
        :return: <str> Hash do bloco
        """
        # Serializa o bloco e gera o hash
        blockString = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(blockString).hexdigest()

    @property
    def lastBlock(self):
        # Retorna o último bloco da blockchain
        return self.chain[-1]

# Instancia o aplicativo Flask
app = Flask(__name__)

# Gera um identificador único para este nó
nodeIdentifier = str(uuid4()).replace('-', '')

# Instancia a classe Blockchain
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    # Endpoint para minerar um novo bloco

    lastBlock = blockchain.lastBlock
    lastProof = lastBlock['proof']
    proof = blockchain.proofOfWork(lastProof)  # Encontra o proof necessário para o novo bloco

    # O minerador recebe uma recompensa (geração de uma nova moeda, "0" significa que a recompensa vem do sistema)
    blockchain.newTransaction(
        sender="0",
        recipient=nodeIdentifier,
        amount=1,
    )

    # Cria o novo bloco e o adiciona à blockchain
    previousHash = blockchain.hash(lastBlock)
    block = blockchain.newBlock(proof, previousHash)

    # Cria a resposta para ser enviada ao cliente
    response = {
        'mensagem': 'Novo bloco forjado',
        'index': block['index'], 
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previousHash': block['previousHash']
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def newTransaction():
    # Endpoint para criar uma nova transação

    values = request.get_json()  # Obtém os dados da requisição

    # Verifica se todos os campos necessários estão presentes
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Faltam valores', 400
    
    # Cria uma nova transação
    index = blockchain.newTransaction(values['sender'], values['recipient'], values['amount'])
    response = {'mensagem': f'Transação será adicionada ao bloco {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def fullChain():
    # Endpoint para exibir a blockchain completa

    response = { 
        'chain': blockchain.chain,
        'length': len(blockchain.chain)  # Retorna o comprimento da blockchain (quantidade de blocos)
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def registerNodes():
    # Endpoint para registrar novos nós na rede

    values = request.get_json()  # Obtém os dados da requisição

    # Obtém a lista de nós a serem registrados
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Por favor, forneça uma lista válida de nós", 400

    # Registra cada nó na lista
    for node in nodes:
        blockchain.registerNode(node)

    response = {
        'mensagem': 'Novos nós foram adicionados',
        'totalNodes': list(blockchain.nodes)
    }
    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    # Endpoint para resolver conflitos de blockchain na rede

    replaced = blockchain.resolveConflicts()

    # Verifica se a blockchain foi substituída por uma mais longa
    if replaced:
        response = {
            'mensagem': 'Nossa chain foi substituída',
            'newChain': blockchain.chain
        }
    else:
        response = {
            'mensagem': 'Nossa chain é autoritativa',
            'chain': blockchain.chain
        }

    return jsonify(response), 200

# Roda o servidor Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
