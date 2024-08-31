# Blockchain em Python

Este projeto implementa uma simples blockchain em Python usando Flask para criar uma API. A blockchain permite adicionar transações, minerar blocos, registrar nós e resolver conflitos entre diferentes blockchains na rede.

## Requisitos

- Python 3.6 ou superior
- Flask
- Requests
- Postman (para enviar requisições HTTP)

## Instalação

1. Clone o repositório:

    ```bash
    git clone https://github.com/Aliragm/Blockchain_study.git
    cd Blockchain_study
    ```

2. Crie um ambiente virtual (opcional, mas recomendado):

    ```bash
    python3 -m venv env
    source env/bin/activate  # No Windows use: env\Scripts\activate
    ```

3. Instale as dependências:

    ```bash
    pip install Flask requests
    ```

4. Execute o servidor Flask:

    ```bash
    python3 app.py
    ```

   O servidor estará rodando em `http://0.0.0.0:5000`.

## Endpoints

### 1. Mineração de Bloco

- **URL:** `/mine`
- **Método:** `GET`
- **Descrição:** Este endpoint realiza a mineração de um novo bloco, resolvendo o problema de Proof of Work e adicionando o bloco à blockchain.

- **Resposta de Sucesso:**
    ```json
    {
      "mensagem": "Novo bloco forjado",
      "index": 2,
      "transactions": [],
      "proof": 35293,
      "previousHash": "1b2c3d..."
    }
    ```

### 2. Criar uma Nova Transação

- **URL:** `/transactions/new`
- **Método:** `POST`
- **Descrição:** Este endpoint cria uma nova transação e a adiciona ao próximo bloco a ser minerado.
- **Corpo da Requisição:**
    ```json
    {
      "sender": "endereço_do_remetente",
      "recipient": "endereço_do_destinatário",
      "amount": 5
    }
    ```
- **Resposta de Sucesso:**
    ```json
    {
      "mensagem": "Transação será adicionada ao bloco 2"
    }
    ```

### 3. Exibir a Blockchain Completa

- **URL:** `/chain`
- **Método:** `GET`
- **Descrição:** Este endpoint retorna a cadeia completa de blocos na blockchain, incluindo todas as transações.

- **Resposta de Sucesso:**
    ```json
    {
      "chain": [
        {
          "index": 1,
          "timestamp": 1628771823.046593,
          "transactions": [],
          "proof": 100,
          "previousHash": "1"
        },
        {
          "index": 2,
          "timestamp": 1628771824.347292,
          "transactions": [
            {
              "sender": "0",
              "recipient": "node_identifier",
              "amount": 1
            }
          ],
          "proof": 35293,
          "previousHash": "1b2c3d..."
        }
      ],
      "length": 2
    }
    ```

### 4. Registrar Novos Nós

- **URL:** `/nodes/register`
- **Método:** `POST`
- **Descrição:** Registra novos nós na rede, adicionando-os à lista de nós conhecidos.

- **Corpo da Requisição:**
    ```json
    {
      "nodes": ["http://192.168.0.5:5000", "http://192.168.0.6:5000"]
    }
    ```
- **Resposta de Sucesso:**
    ```json
    {
      "mensagem": "Novos nós foram adicionados",
      "totalNodes": ["192.168.0.5:5000", "192.168.0.6:5000"]
    }
    ```

### 5. Consenso e Resolução de Conflitos

- **URL:** `/nodes/resolve`
- **Método:** `GET`
- **Descrição:** Este endpoint resolve conflitos de blockchain, garantindo que nossa blockchain seja substituída pela mais longa e válida entre os nós conectados.

- **Resposta de Sucesso (substituída):**
    ```json
    {
      "mensagem": "Nossa chain foi substituída",
      "newChain": [...]
    }
    ```

- **Resposta de Sucesso (não substituída):**
    ```json
    {
      "mensagem": "Nossa chain é autoritativa",
      "chain": [...]
    }
    ```

## Uso com Postman

Você pode usar o Postman para testar os endpoints da API:

1. **Mineração de Bloco:** 
   - Envie uma requisição `GET` para `http://localhost:5000/mine`.
   - Verifique a resposta para ver os detalhes do novo bloco.

2. **Criar Transação:**
   - Envie uma requisição `POST` para `http://localhost:5000/transactions/new`.
   - No corpo da requisição, insira os dados da transação em formato JSON.

3. **Visualizar a Blockchain:**
   - Envie uma requisição `GET` para `http://localhost:5000/chain`.
   - A resposta mostrará todos os blocos da blockchain.

4. **Registrar Novos Nós:**
   - Envie uma requisição `POST` para `http://localhost:5000/nodes/register`.
   - No corpo da requisição, insira os nós a serem registrados.

5. **Resolver Conflitos de Blockchain:**
   - Envie uma requisição `GET` para `http://localhost:5000/nodes/resolve`.
   - Verifique se a blockchain foi substituída ou mantida.

## Contribuição

Sinta-se à vontade para abrir issues ou enviar pull requests para melhorias e correções.
