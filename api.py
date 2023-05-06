from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import configparser as cfg
from datetime import datetime

app = Flask(__name__)

config = cfg.ConfigParser()
config.read('settings.cfg')

app.config['MYSQL_USER'] = config.get('DataBase', 'MYSQL_USER')
app.config['MYSQL_PASSWORD'] = config.get('DataBase', 'MYSQL_PASSWORD')
app.config['MYSQL_DB'] = config.get('DataBase', 'MYSQL_DB')
app.config['MYSQL_CURSORCLASS'] = config.get('DataBase', 'MYSQL_CURSORCLASS')

mysql = MySQL(app)

def db_check_hwid():
    cursor = mysql.connection.cursor()
    query = 'SELECT * FROM auth'
    cursor.execute(query)
    result = cursor.fetchall()

    # Lista de HWIDs permitidos
    allowed_hwids = []

    # Lista de HWIDs com o tempo expirado
    expired_hwids = []

    date = int(datetime.now().timestamp())

    for row in result:
        exp_date = int(row['date'].timestamp())
        if date < exp_date:
            allowed_hwids.append(row['hwid'])
        else:
            expired_hwids.append(row['hwid'])

    cursor.close()
    return allowed_hwids, expired_hwids

def db_get_token(hwid):
    cursor = mysql.connection.cursor()
    query = 'SELECT token FROM auth WHERE hwid = %s'
    cursor.execute(query, (hwid,))
    token = cursor.fetchone()

    if token and token['token'] != '0':
        cursor.close()
        return token['token']
    else:
        query = "UPDATE auth SET token = %s WHERE hwid = %s"
        # Aqui você pode fazer sua lógica de criptografia
        token = hwid[0] + 'api' # Vou apenas adicionar "api" apos o HWID
        value = (token, hwid[0])
        cursor.execute(query, value)
        mysql.connection.commit()
        cursor.close()
        return token

@app.route('/login', methods=['POST'])
def login():
    hwid = request.form.get('hwid')

    allowed_hwids, expired_hwid = db_check_hwid()

    if hwid in allowed_hwids:
        token = get_token(hwid)
        return jsonify({'token': token}), 200
    else:
        if hwid in expired_hwid:
            return jsonify({'error': 'Licença expirada'}), 401
        else:
            return jsonify({'error': 'HWID inválido'}), 401

@app.route('/verify', methods=['POST'])
def verify():
    token = request.form.get('token')
    hwid = request.form.get('hwid')

    if verify_token(token, hwid):
        return jsonify({'message': 'HWID verificado'}), 200
    else:
        return jsonify({'error': 'Token ou HWID inválido'}), 401

def get_token(hwid):
    # função para pegar/gerar token de autenticação
    return db_get_token(hwid)

def verify_token(token, hwid):
    # função para verificar se o token é válido.
    return token == get_token(hwid)

if __name__ == '__main__':
    app.run()
