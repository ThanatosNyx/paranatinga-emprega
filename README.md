# Paranatinga Emprega

Plataforma web comunitária para conexão entre trabalhadores, empresas e profissionais autônomos no município de Paranatinga - MT.

---

## Sobre o Projeto

O Paranatinga Emprega foi desenvolvido para centralizar as oportunidades de trabalho da região em um único canal simples, gratuito e de fácil acesso. A plataforma permite a publicação de vagas formais, trabalhos temporários e a divulgação de serviços prestados por profissionais autônomos locais.

### Contexto Acadêmico

Este sistema foi desenvolvido como Atividade Prática Extensionista do curso de Análise e Desenvolvimento de Sistemas da Faculdade UNINTER. O projeto está alinhado ao Objetivo de Desenvolvimento Sustentável 8 (ODS 8) da ONU — *Trabalho Decente e Crescimento Econômico*, visando o apoio ao mercado de trabalho local.

---

## Funcionalidades Principais

* **Busca e Filtros Interativos:** Pesquisa por palavra-chave e filtragem dinâmica por categorias para vagas e serviços autônomos.
* **Publicação Direta:** Formulários simplificados para anúncio de vagas e profissionais de forma rápida.
* **Painel Administrativo e Moderação:** Área restrita para aprovação, edição e exclusão de publicações antes de irem ao ar.
* **Navegação Condicional:** Exibição dinâmica de links de gestão (Admin e Botão Sair) apenas para usuários autenticados.
* **Interface Responsiva:** Layout adaptado para navegação em dispositivos móveis e desktop.

---

## Tecnologias Utilizadas

* **Back-end:** Python, Flask
* **Front-end:** HTML5, CSS3, JavaScript (Vanilla), Jinja2 (Template Engine)
* **Banco de Dados:** SQLite (`banco.db`)

---

## Acesso ao Painel Administrativo 

Para testar o fluxo de moderação de conteúdo (aprovação de cadastros pendentes, edição ou exclusão de postagens):

* **Rota de Acesso:** `http://127.0.0.1:5000/login` (ou `/admin`)
* **Usuário:** `admin`
* **Senha:** `admin123`

*Nota: Por boas práticas de usabilidade e segurança, os botões de gerenciamento só ficam visíveis no menu principal após a realização do login.*

---

## Como Executar o Projeto Localmente

O repositório já inclui o arquivo `banco.db` inicial configurado para testes da banca.

1. **Baixar o Repositório:**
   Faça o download do arquivo `.zip` do projeto e extraia o conteúdo em seu computador.

2. **Instalar as dependências:**
   Abra o terminal na pasta raiz do projeto e execute:
   ```bash
   pip install flask
