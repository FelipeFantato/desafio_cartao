# Desafio Hyperativa

Este projeto é uma implementação de uma API Flask que consome dados de um banco de dados PostgreSQL, utilizando SQLAlchemy para a conexão com o banco.

## Pré-requisitos

Para rodar este projeto, você precisará ter o Docker e o Docker Compose instalados em sua máquina.

## Instruções de Uso

1. Clone o repositório para a sua máquina local.
2. Navegue até o diretório do repositório clonado.
3. Execute o comando abaixo no terminal:

```bash
docker build -t desafiohyperativa-app .
docker compose up
```
  Utilize o login:hyperativa
            senha:2Mr2g1
  Para se conectar a API.

- Realizar login em /login, retorna chave JWT 
- Ao utilizar /upload, é possível cadastrar uma lista de itens, passando o token(JWT) na Query;
