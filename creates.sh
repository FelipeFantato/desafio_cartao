psql -h localhost -U postgres -c "\c hyperativadb" -c " CREATE TABLE IF NOT EXISTS users(usuario varchar, senha varchar);" 
psql -h localhost -U postgres -c "\c hyperativadb" -c " CREATE TABLE IF NOT EXISTS tabela_cartao(cod_cartao int,num_lote int, nome varchar, data date, lote varchar);" 
 