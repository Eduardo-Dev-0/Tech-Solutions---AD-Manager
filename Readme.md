<div align="center">

<img src="icons/icone_ad_manager.ico" width="100" alt="AD Manager Logo"/>

# Tech Solutions — AD Manager

**Ferramenta gráfica para gerenciamento de usuários no Active Directory via planilha Excel**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Plataforma-Windows-0078D6?logo=windows&logoColor=white)
![License](https://img.shields.io/badge/Licença-MIT-green)
![Status](https://img.shields.io/badge/Status-Ativo-brightgreen)

</div>

---

## 📌 Sobre o Projeto

O **Tech Solutions AD Manager** é uma ferramenta desktop desenvolvida em **Python + CustomTkinter** que permite gerenciar usuários do **Active Directory em lote**, importando os dados diretamente de uma planilha Excel.

Ideal para administradores de TI que precisam criar, ativar, desativar ou remover múltiplos usuários de forma rápida, controlada e auditável — sem precisar acessar o ADUC manualmente para cada conta.

---

## ✨ Funcionalidades

### 🔌 Conexão com o AD
- Detecção automática do domínio AD da máquina via FQDN
- Seleção dinâmica da OU de destino com campo de busca em tempo real
- Movimentação de usuários entre OUs diretamente pela ferramenta

### 📋 Importação de Dados
- Importação via planilha Excel (`.xlsx` / `.xls`)
- Detecção automática da linha de cabeçalho
- Suporte a colunas: **Nome**, **CPF** e **Matrícula** (opcional)
- Validação matemática de CPF (dígitos verificadores)
- Detecção de logins duplicados dentro da própria planilha
- Notificação detalhada de erros linha a linha

### ⚙️ Configurações de Login e Senha
- Formato de login totalmente configurável por blocos:
  - `Primeiro Nome`, `Último Nome`, `Todos os Nomes`
  - `CPF (4, 6 ou 11 dígitos)`, `Matrícula`
  - Separadores: nenhum, `.` ou `_`
- Formato de senha configurável por blocos:
  - CPF, Nome, Senha Fixa customizável
- Preview em tempo real com nome e CPF de exemplo
- Padrão original restaurável com um clique
- Limite de 20 caracteres do AD respeitado automaticamente

### 👥 Operações em Lote
- Seleção individual por checkbox por linha
- Seleção/desmarcação em massa com botões rápidos
- **Verificar** — checa existência no AD antes de qualquer ação
- **Criar** — cria usuários com login, senha e displayName configurados
- **Ativar / Desativar** — habilita ou desabilita contas
- **Remover** — exclusão com confirmação obrigatória
- **Redefinir Senha** — redefine em lote sem recriar a conta
- **Mover OU** — move usuários selecionados para outra OU

### 📊 Relatórios e Auditoria
- Coluna de **Senha Inicial** visível na tabela antes de criar
- **Exportar Relatório** — gera `.xlsx` com Nome, Login, Senha e Status
- **Log com cores** — ✔ verde / ⚠ laranja / ✖ vermelho
- **Exportar Log** — salva `.txt` com data e hora no nome
- **Limpar Log** — limpeza rápida da área de log
- **Rodapé de status** — contador em tempo real: Total | Selecionados | Criados | Erros
- **Barra de progresso** — visível durante operações em lote

---

## 🖥️ Interface

```
┌─────────────────────────────────────────────────────────────────┐
│  Tech Solutions - Gerenciador AD              ⚙ Configurações   │
├─────────────────────────────────────────────────────────────────┤
│  🔎 Detectar Domínio  │  dominio.local  │  📂 Selecionar OU     │
├─────────────────────────────────────────────────────────────────┤
│  📂 Selecionar Planilha   caminho/arquivo.xlsx   📊 Exportar    │
├─────────────────────────────────────────────────────────────────┤
│  ☑ Selecionar Todos   ☐ Desselecionar Todos                     │
├──────┬──────────────┬─────────────┬─────────────┬──────┬───────┤
│  ☑   │ Nome         │ CPF         │ Login       │ Senha│Status │
├──────┼──────────────┼─────────────┼─────────────┼──────┼───────┤
│  ☑   │ João Silva   │ 123.456.789 │ joaosilva12 │ ...  │ ✔     │
│  ☐   │ Maria Souza  │ 987.654.321 │ mariasouza98│ ...  │ ✔     │
├─────────────────────────────────────────────────────────────────┤
│ Verificar │ Criar │ Desativar │ Ativar │ Remover │ 🔑 │ 📁 OU  │
├─────────────────────────────────────────────────────────────────┤
│ ████████████████░░░░░░  18 / 25                                  │
├─────────────────────────────────────────────────────────────────┤
│ 📋 Log de Operações              💾 Exportar Log  🗑 Limpar Log  │
│ ✔ Usuário criado: joaosilva1234                                  │
│ ⚠ Login ajustado (limite 20): ...                               │
│ ✖ Erro ao criar mariasouza9876: ...                             │
├─────────────────────────────────────────────────────────────────┤
│ Total: 25  │  Selecionados: 18  │  Criados: 17  │  Erros: 1     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Estrutura do Projeto

```
AD-Manager/
│
├── GerenciadorAD.py        # Código principal da aplicação
├── requirements.txt        # Dependências Python
├── README.md               # Este arquivo
├── .gitignore              # Arquivos ignorados pelo Git
│
├── icons/                  # Ícones da interface
│   ├── icone_ad_manager.ico
│   ├── selecionar.ico
│   ├── verificar.ico
│   ├── criar.ico
│   ├── desativar.ico
│   ├── ativar.ico
│   └── remover.ico
│
├── dist/                   # Executável gerado (não versionado)
│   └── GerenciadorAD.exe
│
└── instalador/             # Script Inno Setup
    └── setup.iss
```

---

## 📋 Estrutura da Planilha

A planilha deve conter ao menos as colunas **Nome** e **CPF**. A coluna **Matrícula** é opcional.

| Nome         | CPF             | Matrícula |
|--------------|-----------------|-----------|
| João Silva   | 123.456.789-00  | 2024001   |
| Maria Souza  | 987.654.321-00  | 2024002   |

**Regras:**
- Nome deve conter ao menos **primeiro e último nome**
- CPF deve ter **11 dígitos válidos** (com ou sem formatação) — validação dos dígitos verificadores incluída
- A ferramenta detecta automaticamente a linha de cabeçalho
- A leitura para ao encontrar uma linha iniciando com **"Total"**
- Linhas com erro são destacadas e detalhadas no log

---

## 🔐 Geração de Login e Senha

O formato é **totalmente configurável** pela janela ⚙ Configurações. O padrão é:

```
Login : primeiro_nome + ultimo_nome + 4 primeiros dígitos do CPF
Senha : CPF completo (11 dígitos, sem formatação)
```

**Exemplo com padrão:**
```
Nome  : João Silva
CPF   : 123.456.789-00

Login : joaosilva1234
Senha : 12345678900
```

**Outros formatos possíveis:**
```
Login : joao.silva       (primeiro_nome + "." + ultimo_nome)
Login : joaosilva123456  (primeiro_nome + ultimo_nome + cpf_6)
Senha : Tech@2026        (senha fixa)
Senha : Tech@1234        (senha fixa + cpf_4)
```

---

## ⚙️ Requisitos do Sistema

| Requisito       | Detalhe                                      |
|-----------------|----------------------------------------------|
| Sistema         | Windows 10 ou superior                       |
| Python          | 3.8 ou superior                              |
| Rede            | Conectado ao domínio Active Directory        |
| Permissões AD   | Criar, ativar, desativar e remover usuários  |

---

## 🚀 Instalação e Execução

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/ad-manager.git
cd ad-manager
```

### 2. Crie um ambiente virtual (recomendado)

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Execute a aplicação

```bash
python GerenciadorAD.py
```

> ⚠️ O computador precisa estar **conectado ao domínio AD** e o usuário deve ter **permissões de gerenciamento de usuários**.

---

## 📦 Gerar Executável (.exe)

```bash
python -m PyInstaller --onefile --noconsole ^
  --icon=icons/icone_ad_manager.ico ^
  --add-data "icons;icons" ^
  GerenciadorAD.py
```

O executável será gerado em `dist\GerenciadorAD.exe`.

---

## 🛠️ Gerar Instalador

O projeto usa **Inno Setup** para gerar um instalador Windows.

1. Instale o [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Abra o arquivo `instalador/setup.iss`
3. Compile — o instalador será gerado como `TechSolutions_AD_Manager_Setup.exe`

---

## 📦 Dependências

| Biblioteca      | Versão   | Uso                                      |
|-----------------|----------|------------------------------------------|
| customtkinter   | 5.2.2    | Interface gráfica moderna                |
| pandas          | 2.2.2    | Leitura e manipulação de planilhas Excel |
| pillow          | 10.3.0   | Carregamento de ícones e imagens         |
| unidecode       | 1.3.8    | Remoção de acentos para login            |
| pyad            | 0.6.0    | Integração LDAP com Active Directory     |
| openpyxl        | 3.1.2    | Suporte a arquivos .xlsx                 |
| xlrd            | 2.0.1    | Suporte a arquivos .xls legados          |

---

## 🗺️ Roadmap

- [x] Detecção automática de domínio AD
- [x] Seleção de OU com campo de busca
- [x] Importação via planilha Excel
- [x] Validação matemática de CPF
- [x] Detecção de logins duplicados
- [x] Formato de login e senha configurável
- [x] Seleção individual por checkbox
- [x] Barra de progresso em operações em lote
- [x] Log com cores e exportação
- [x] Exportação de relatório Excel
- [x] Redefinir senha em lote
- [x] Mover usuários entre OUs
- [ ] Suporte a múltiplos domínios
- [ ] Importação de foto de perfil do usuário
- [ ] Histórico de operações persistente

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Siga os passos abaixo:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/minha-feature`)
3. Commit suas mudanças (`git commit -m 'feat: adiciona minha feature'`)
4. Push para a branch (`git push origin feature/minha-feature`)
5. Abra um Pull Request

---

## 📄 Licença

Distribuído sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👤 Autor

**Eduardo Gabriel de Meneses**

Desenvolvido para automação de gerenciamento de usuários no Active Directory.
Mantido e evoluído pela **Tech Solutions**.

---

<div align="center">

Feito com Dedicação e Python

</div>