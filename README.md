# Sistema de Compartilhamento P2P (Peer-to-Peer)

## Descrição do Projeto

Este projeto implementa um sistema de compartilhamento de arquivos peer-to-peer desenvolvido em Python. O sistema permite que múltiplos peers se conectem em uma rede descentralizada para descobrir, listar e baixar arquivos uns dos outros, utilizando relógios lógicos de Lamport para sincronização distribuída.

## Funcionalidades Implementadas

### 1. **Arquitetura P2P Básica**
- Sistema descentralizado onde cada peer atua simultaneamente como cliente e servidor
- Descoberta automática de peers na rede
- Gerenciamento de status dos peers (ONLINE/OFFLINE)
- Comunicação via sockets TCP

### 2. **Relógio Lógico de Lamport**
- Implementação completa dos relógios lógicos para sincronização distribuída
- Atualização automática dos relógios em todas as mensagens trocadas
- Manutenção da causalidade entre eventos na rede

### 3. **Descoberta e Listagem de Arquivos**
- Comando `LS` para listar arquivos disponíveis em peers remotos
- Exibição de informações detalhadas (nome, tamanho em bytes, peer origem)
- Interface interativa para seleção de arquivos

### 4. **Transferência de Arquivos**
- Sistema de download (`DL`) com codificação Base64
- Transferência segura de arquivos binários
- Salvamento automático no diretório compartilhado local

### 5. **Gerenciamento de Peers**
- Lista de peers conhecidos com status e informações de relógio
- Adição automática de novos peers descobertos na rede
- Persistência da lista de peers em arquivo de configuração
- Comando `GET_PEERS` para descobrir peers transitivamente

### 6. **Protocolo de Comunicação**
Mensagens implementadas:
- **HELLO**: Anúncio de presença na rede
- **RETURN_HELLO**: Confirmação de recebimento
- **GET_PEERS**: Solicitação de lista de peers conhecidos
- **PEER_LIST**: Resposta com lista de peers
- **LS**: Solicitação de lista de arquivos
- **LS_LIST**: Resposta com arquivos disponíveis
- **DL**: Solicitação de download de arquivo específico
- **FILE**: Envio do arquivo codificado
- **BYE**: Notificação de saída da rede

## Estrutura do Código

### `Class.py`
Contém as principais classes do sistema:

- **`Clock`**: Implementa o relógio lógico de Lamport
  - `incrementClock()`: Incrementa o relógio local
  - `updateClock()`: Atualiza baseado em relógio recebido

- **`Peer`**: Classe principal do peer
  - Gerenciamento de conexões TCP
  - Processamento de mensagens (`tratar_mensagem()`)
  - Envio de mensagens (`send_message()`)
  - Manutenção da lista de peers conhecidos

### `eachare.py`
Arquivo principal com:
- Interface de linha de comando
- Validação de parâmetros de entrada
- Menu interativo para operações
- Funções auxiliares para listagem e gerenciamento

## Como Usar

### Execução
```bash
python3 eachare.py <endereço>:<porta> <arquivo_vizinhos> <diretório_compartilhado>
```

**Exemplo:**
```bash
python3 eachare.py 127.0.0.1:5001 vizinhos.txt diretorio_compartilhado
```

### Parâmetros
- **`endereço:porta`**: IP e porta onde o peer será executado
- **`arquivo_vizinhos`**: Arquivo texto contendo lista inicial de peers (formato `ip:porta`)
- **`diretório_compartilhado`**: Pasta local com arquivos para compartilhar

### Menu de Comandos
1. **Listar peers**: Mostra peers conhecidos e permite conexão
2. **Obter peers**: Descobre novos peers transitivamente
3. **Listar arquivos locais**: Exibe arquivos do diretório local
4. **Buscar arquivos**: Procura arquivos em peers remotos
5. **Exibir estatísticas**: Mostra informações de relógios e peers
6. **Alterar tamanho de chunk**: (Não implementado)
9. **Sair**: Encerra o peer e notifica a rede

## Arquivos de Configuração

### `vizinhos.txt` / `vizinhos2.txt`
Contém lista inicial de peers no formato:
```
127.0.0.1:8001
127.0.0.1:8002
192.168.1.100:8003
```

## Funcionalidades Avançadas

### Sincronização Distribuída
- Todos os peers mantêm relógios lógicos sincronizados
- Cada mensagem carrega timestamp lógico
- Garantia de ordenação causal de eventos

### Descoberta Transitiva
- Peers descobrem automaticamente outros peers na rede
- Propagação de informações de conectividade
- Adição automática de novos peers ao arquivo de configuração

### Interface Rica
- Menu interativo com formatação tabulada
- Exibição detalhada de arquivos com tamanhos
- Seleção numérica para downloads

## Estado Atual do Desenvolvimento

O sistema está funcional com todas as funcionalidades básicas implementadas:
- ✅ Comunicação P2P estabelecida
- ✅ Relógios lógicos funcionando
- ✅ Descoberta de peers operacional
- ✅ Transferência de arquivos completa
- ✅ Interface de usuário implementada
- ✅ Tratamento de erros e conexões
- ⏳ Otimizações e melhorias em andamento

## Tecnologias Utilizadas
- **Python 3**: Linguagem principal
- **Sockets TCP**: Comunicação em rede
- **Threading**: Processamento concorrente
- **Base64**: Codificação para transferência de arquivos
- **Sistema de arquivos**: Gerenciamento de diretórios e arquivos

## Autores
- Pedro Fioravanti
- Oliver Kuramae

---
*Projeto desenvolvido para a disciplina ACH2147 - Redes de Computadores*
