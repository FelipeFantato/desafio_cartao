from flask import Flask, jsonify, request, make_response
from functools import wraps
import jwt
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'

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

@app.route('/nao_protegido', methods=['GET'])
def nao_protegido():
    return jsonify({'mensagem': 'Qualquer um pode ver isso!'})

@app.route('/protegido', methods=['GET'])
@token_required
def protegido():
    return jsonify({'mensagem': 'Parabéns! Você conseguiu ver uma mensagem protegida'})

@app.route('/login', methods=['POST'])
def login():
    auth = request.authorization
    if auth:
        user = auth.username
        pwd = auth.password

        if user and pwd:
            #consulta banco
            #hash bate com o que ta no banco

            #hashBanco = getHashdb(user)    
            hashBanco = hash(pwd)
            if hashBanco and hashBanco == hash(pwd):
                token = jwt.encode({
                    'user': auth.username,
                    'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=30)
                }, app.config['SECRET_KEY'], algorithm="HS256")
                print( datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=30))
                return jsonify({'token': token})

    return make_response('Não foi possível verificar!', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

def processar_linha(linhas):
    
    primeiraLinha = linhas[0]
    #trata primeira linha
    ultimaLinha = linhas[-1]
    #trata ultima linha

    linhas = linhas[1:len(linhas)-1]
    for linha in linhas:
        pass


    # Remover comentários e espaços extras
    linha = linha.split('//')[0].strip()
    if linha.startswith('DESAFIO-HYPERATIVA'):
        nome = linha[0:29].strip()
        data = linha[29:37].strip()
        lote = linha[37:45].strip()
        qtd_registros = linha[45:51].strip()
        return f'Nome: {nome}, Data: {data}, Lote: {lote}, Qtd Registros: {qtd_registros}'
    elif linha.startswith('C'):
        identificador = linha[0:2].strip()
        numeracao_lote = linha[2:9].strip()
        numero_cartao = linha[9:].strip().ljust(19)  # Preencher com espaços até a coluna 26
        return f'Identificador: {identificador}, Numeração no Lote: {numeracao_lote}, Número de Cartão: {numero_cartao}'
    elif linha.startswith('LOTE'):
        lote = linha[0:8].strip()
        qtd_registros = linha[8:14].strip()
        return f'Lote: {lote}, Qtd Registros: {qtd_registros}'
    else:
        return 'Linha não reconhecida'

@app.route('/upload', methods=['POST'])
@token_required
def upload_file():
    if request.files == []:
        print(request.files)
        return 'Nenhum arquivo enviado', 400
    file = request.files['file']
    if file.filename == '':
        return 'Nenhum arquivo selecionado', 400
    if file and file.filename.endswith('.txt'):
        content = file.read().decode('utf-8')
        linhas = content.strip().split('\n')
        resultados = processar_linha(linhas)
        resultado_final = '\n'.join(resultados)
        print(resultado_final)
        # Aqui você pode processar o conteúdo do arquivo como desejar
        return resultado_final, 200
    elif request.data:
        text_content = request.data.decode('utf-8')

    else:
        return 'Tipo de arquivo inválido', 400

if __name__ == '__main__':
    app.run(debug=True)