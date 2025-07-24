# Gerador de QR Code Avançado

[![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Tkinter](https://img.shields.io/badge/GUI-Tkinter-lightgrey?style=flat-square&logo=tcl)](https://docs.python.org/3/library/tkinter.html)
[![Pillow](https://img.shields.io/badge/Image%20Processing-Pillow-darkgreen?style=flat-square&logo=python)](https://python-pillow.org/)
[![QR Code Generation](https://img.shields.io/badge/QR%20Code-qrcode-orange?style=flat-square)](https://pypi.org/project/qrcode/)
[![Database-SQLite](https://img.shields.io/badge/Database-SQLite-07405E?style=flat-square&logo=sqlite&logoColor=white)](https://www.sqlite.org/index.html)
[![Windows Clipboard](https://img.shields.io/badge/Windows%20Clipboard-pywin32-informational?style=flat-square)](https://pypi.org/project/pywin32/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

Este é um aplicativo de desktop em Python para a geração de QR Codes personalizáveis, com gerenciamento de histórico e diversas opções de usabilidade.

## Funcionalidades

O aplicativo oferece as seguintes funcionalidades principais:

* **Geração de QR Codes:** Crie QR Codes a partir de texto ou URLs.
* **Personalização Visual:**
    * Escolha a cor do QR Code e a cor de fundo.
    * Defina o nível de correção de erro (L, M, Q, H), que afeta a densidade e robustez do QR Code.
    * Adicione uma imagem de logo personalizada no centro do QR Code.
* **Gerenciamento de Histórico:**
    * Todos os QR Codes gerados são automaticamente salvos em um histórico persistente (SQLite).
    * Visualize o histórico com o nome do arquivo, data de criação, cores e nível de erro.
    * Carregue um QR Code do histórico para visualização e edição dos campos.
    * **Seção de Histórico Ocultável:** A seção de histórico pode ser mostrada ou ocultada através de um botão dedicado, otimizando o espaço da interface.
* **Edição de QR Codes:**
    * Selecione um item do histórico, modifique seus dados e salve as alterações. Um novo QR Code será gerado e substituirá o antigo no histórico e no disco.
* **Opções de Saída e Compartilhamento:**
    * **Salvar Como:** Exporte o QR Code gerado para um local específico no seu computador, com um nome de arquivo personalizado.
    * **Copiar Imagem:** Copie a imagem do QR Code atualmente exibido para a área de transferência do sistema (funcionalidade completa para Windows, fallback para outras plataformas).
    * **Abrir Local do Arquivo:** Abra o diretório onde o QR Code exibido está salvo diretamente pelo aplicativo.
* **Usabilidade Aprimorada:**
    * **Layout Estável:** Elementos da interface com tamanhos mais fixos e comportamento previsível ao redimensionar a janela.
    * **Validação de Entrada:** Verifica se os campos de texto/URL e nome do arquivo não estão vazios e sanitiza nomes de arquivo para evitar caracteres inválidos.
    * **Limpeza de Campos:** Botão para limpar rapidamente todos os campos de entrada e opções de personalização.
    * **Pré-visualização:** Exibe a versão do QR Code e o nível de correção de erro aplicado após a geração.
* **Atalhos de Teclado:**
    * `Ctrl + G`: Gerar Novo QR Code
    * `Ctrl + S`: Salvar Como...
    * `Ctrl + L`: Limpar Campos
    * `Ctrl + C`: Copiar Imagem

## Estrutura do Projeto

O projeto segue uma estrutura modular para melhor organização e manutenção:

``` 
QRcodeGenerator/
├── .venv/                      # Ambiente virtual
├── src/                        # Código-fonte da aplicação
│   ├── init.py             # Torna 'src' um pacote Python
│   ├── config.py               # Configurações de diretórios e paths
│   ├── db_manager.py           # Funções de gerenciamento do banco de dados SQLite
│   ├── qr_logic.py             # Lógica de geração e salvamento de QR Codes
│   └── qr_app.py               # Interface Gráfica do Usuário (GUI principal)
├── data/                       # Arquivos de dados
│   ├── db/
│   │   └── historico_qr_codes.db # Banco de dados SQLite do histórico
│   └── icons/
│       └── logo.png            # Ícone da janela do aplicativo
├── images/                     # Imagens geradas pelo aplicativo
│   └── generated_qrs/          # QR Codes salvos automaticamente
├── temp_clipboard/             # Arquivos temporários para a funcionalidade de copiar imagem
├── README.md                   # Este arquivo
└── requirements.txt            # Dependências do projeto
``` 
## Instalação

Siga estes passos para configurar e instalar o projeto:

1.  **Clone o Repositório** (ou baixe os arquivos):
    ```bash
    git clone https://github.com/amaro-netto/QRcodeGenerator
    cd QRcodeGenerator
    ```

2.  **Crie e Ative um Ambiente Virtual:**
    É altamente recomendado usar um ambiente virtual para gerenciar as dependências do projeto.
    ```bash
    python -m venv .venv
    ```
    * **Windows (Cmd/PowerShell):**
        ```bash
        .\.venv\Scripts\activate
        ```
    * **Linux/macOS (Bash/Zsh):**
        ```bash
        source ./.venv/bin/activate
        ```

3.  **Instale as Dependências:**
    Crie um arquivo `requirements.txt` na **raiz do projeto** com o seguinte conteúdo:
    ```
    Pillow
    qrcode
    pywin32;platform_system=="Windows"
    ```
    Em seguida, instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Prepare os Diretórios de Dados e Ícone:**
    Os diretórios `data/db/`, `data/icons/`, `images/generated_qrs/` e `temp_clipboard/` serão criados automaticamente na primeira execução, mas você deve preparar o ícone:
    * Converta sua logo para `logo.png`.
    * Coloque `logo.png` dentro de `data/icons/`.

## Uso

Para executar o aplicativo, certifique-se de que seu ambiente virtual esteja ativado e você esteja na **raiz do projeto**:

```bash
python -m src.qr_app
```

## Contribuição

Sinta-se à vontade para contribuir com melhorias, relatar bugs ou sugerir novos recursos.

## Licença

Este projeto está licenciado sob a MIT License.
