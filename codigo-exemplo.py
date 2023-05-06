import wmi
import requests

print("Carregando...")

hwid = wmi.WMI().Win32_ComputerSystemProduct()[0].UUID

print('Seu HWID:',hwid)

login_response = requests.post('http://localhost:5000/login', data={'hwid': hwid})

if login_response.status_code == 200:
    token = login_response.json()['token']
    check = requests.post('http://localhost:5000/verify', data={'token': token, 'hwid': hwid})

    if check.status_code == 200:
        print('HWID verificado com sucesso! Seu token:', token)
    else:
        print('Erro ao verificar HWID:', check.json()['error'])

elif login_response.status_code == 401:
    print('Erro:', login_response.json()['error'])
    
else:
    print('Erro ao acessar o servidor')
