from flask import Flask, jsonify, request, make_response
from functools import wraps
import jwt
import datetime
from sqlalchemy import  create_engine, Column, Integer, String, Date, Table, MetaData
from sqlalchemy import text as transformText
from sqlalchemy.exc import OperationalError
import time
import logging

usuario = 'postgres'
senha = '0e6VfE2Mr2g1'
host = 'postgres'
porta = '5432'
banco_de_dados = 'hyperativadb'

conexao_db = f'postgresql://{usuario}:{senha}@{host}:{porta}/{banco_de_dados}'
engine = create_engine(conexao_db)

# Tentar conectar várias vezes com intervalo de 5 segundos
max_tentativas = 10
tentativa_atual = 0

while tentativa_atual < max_tentativas:
    try:
        conn = engine.connect()
        print("Conexão com o banco de dados estabelecida com sucesso.")
        break 
    except OperationalError as e:
        print(f"Falha ao conectar: {e}. Tentando novamente em 5 segundos.")
        time.sleep(5) 
        tentativa_atual += 1

if tentativa_atual == max_tentativas:
    print("Não foi possível estabelecer uma conexão com o banco de dados.")



metadata = MetaData()

# Definir a tabela users
users = Table('users', metadata,
              Column('usuario', String),
              Column('senha', String))

# Definir a tabela tabela_cartao
tabela_cartao = Table('tabela_cartao', metadata,
                      Column('cod_cartao', String),
                      Column('num_lote', String),
                      Column('nome', String),
                      Column('data', String),
                      Column('lote', String))

# Criar as tabelas no banco de dados
metadata.create_all(engine)

comando_insert = transformText(f"INSERT INTO users VALUES ('hyperativa', {hash('2Mr2g1')})")
resultado = conn.execute(comando_insert)
conn.commit()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'



# Configure Flask logging
app.logger.setLevel(logging.INFO)  # Set log level to INFO
handler = logging.FileHandler('app.log')  # Log to a file
app.logger.addHandler(handler)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')  # http://127.0.0.1:5000/rota?token=xxxxxx

        if not token:
            return jsonify({'alerta': 'Token está faltando!'}), 403

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except Exception as e:
            return jsonify({'alerta': 'Token é inválido!', 'error' : str(e)}), 403

        return f(*args, **kwargs)

    return decorated

@app.route('/pesquisar', methods=['POST'])
@token_required
def pesquisar():
    #cod_cartao int,num_lote int, nome varchar, data date, lote varchar);" 
    if request.data:
        text_content = request.data.decode('utf-8')

        comando_insert = transformText(f"select * from tabela_cartao where cod_cartao = '{text_content}'")
        resultado = conn.execute(comando_insert)
        resultado = resultado.fetchall()
        
        if resultado:
            return jsonify({'Está cadastrado!': str(resultado)})
        else:
            return jsonify({'Não cadastrado!': str(resultado)})
    else:
        return jsonify({'Deu erro!': str(resultado)})

@app.route('/cadastrar', methods=['POST'])
@token_required
def protegido():
    #cod_cartao int,num_lote int, nome varchar, data date, lote varchar);" 
    if request.data:
        text_content = request.data.decode('utf-8')

        comando_insert = transformText(f"INSERT INTO tabela_cartao VALUES ('{text_content}', '', '', NOW(), '')")
        resultado = conn.execute(comando_insert)
        conn.commit()
    
        return jsonify({'inserido com sucesso!': str(resultado)})
    else:
        return jsonify({'Deu erro!': str(resultado)})

@app.route('/login', methods=['POST'])
def login():
    auth = request.authorization
    if auth:
        user = auth.username
        pwd = auth.password

        if user and pwd:
            resultado = conn.execute(transformText(f"SELECT usuario, senha FROM users where usuario ='{user}'"))
            resultado = resultado.fetchall()


            hashBanco = None
            app.logger.info(resultado)
            app.logger.info(hash(pwd))
            
            if resultado:
                
                if resultado[0].usuario == user:
                    #encontrou usuario
                    hashBanco = resultado[0].senha


            if hashBanco and hashBanco == str(hash(pwd)):
                token = jwt.encode({
                    'user': auth.username,
                    'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=30)
                }, app.config['SECRET_KEY'], algorithm="HS256")

                return jsonify({'token': token})

    return make_response('Não foi possível verificar!', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

def processarArquivo(linhas):
    
    resultado = ''
    #trata primeira linha
    primeiraLinha = linhas[0]
    nome = primeiraLinha[0:29].strip()
    data = primeiraLinha[29:37].strip()
    lote = primeiraLinha[37:45].strip()
    qntdRegistros = primeiraLinha[45:51].strip()


    #trata ultima linha
    ultimaLinha = linhas[-1]
    lote = ultimaLinha[0:8].strip()
    qtdRegistrosFin = ultimaLinha[8:14].strip()


    linhas = linhas[1:len(linhas)-1]
    listaSql = []
    for linha in linhas:
        identificador = linha[0:1].strip()

        if identificador and identificador == 'C':
            #é cartao
            numLote = linha[1:7].strip()
            numCartao = linha[7:26].strip()
            sql = f"insert into tabela_cartao values('{numCartao}','{numLote}','{nome}','{data}' ,'{lote}')" 
            listaSql.append(sql)
    return listaSql


# @app.route('/consultar', methods=['POST'])
# @token_required
# def consulta_cartao():

@app.route('/upload', methods=['POST'])
@token_required
def upload_file():
    
        
    if 'text' in request.form:
        text = request.form['text']

        try:
            inteiroCartao = int(text)

            comando_insert = transformText(f"INSERT INTO tabela_cartao VALUES ({inteiroCartao}, '', '', NOW(), '')")
            conn.execute(comando_insert)
            return str("Adicionado com sucesso!"), 200
        except:
            return 'Texto inválido, favor inserir apenas números', 400

    elif request.data:
        text_content = request.data.decode('utf-8')

   
    if request.files == []:
        print(request.files)
        return 'Nenhum arquivo enviado', 400
    file = request.files['file']
    if file.filename == '':
        return 'Nenhum arquivo selecionado', 400

    if file and file.filename.endswith('.txt'):
        content = file.read().decode('utf-8')
        linhas = content.strip().split('\n')
        inserts = processarArquivo(linhas)

        for insert in inserts:
            conn.execute(transformText(insert))
            conn.commit()
        return "Cartões inseridos com sucesso!", 200
    else:
        return 'Tipo de arquivo inválido', 400
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    app.run(debug=True)

conn.close()
