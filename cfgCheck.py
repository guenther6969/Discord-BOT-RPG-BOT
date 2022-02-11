# imports
import os 
import msvcrt
import sys
import json
import time
import subprocess

def createCFGfile():
    # Printizinhos para ficar bonito
    print('\n\n')
    print(' >|')
    print("  | Não foi possivel encontrar o arquivo 'config.json' !")
    print("  | Gostaria de criar esse arquivo automaticamente ? [ S / N ] ", end=' ', flush=True)

    # Pega a primeira tecla de input que o usuario precionou
    char = msvcrt.getch().lower()

    # Se a tecla for X:
    if char == b's':
        print('S')
        time.sleep(0.5)
        print('  | Criando o arquivo de configuração', end='', flush=True)
        
        print('.', end='', flush=True)
        print('.', end='', flush=True)
        print('.', end='\n', flush=True)

        # Abre, ja criando, o config.json
        try:
            f = open("config.json", "x")
            # e escreve nele as informações básicas
            with open("config.json", "a") as f:
                f.write("""
{
  "prefix": "!",
  "token": "TOKEN",
  "permissions": "8",

  "application_id": "APP_ID",

  "owners": [
    "OWNER_ID"
  ]
}
"""
    )

            print('  | Arquivo criado com sucesso !')
            print('  | Gostaria de abrir o arquivo para preenchera as informações necesarias? [ S / N ] ')
            
            # Outro keyboard catch, dessa vez para ver se o usuario que abrir o arquivo recem criado
            char = msvcrt.getch().lower()
            
            # Caso sim
            if char == b's':
                print('  | Abrindo config.json . . . ')
                
                # Chama o          cmd\/      \/executando um comando\/ que no caso é chamar o bloco de notas no config.json
                subprocess.call(['cmd.exe', '/c', 'notepad config.json'])

                # subprocess.Popen(['cmd.exe', '/c', 'notepad config.json']) 
                # sbp.call() espera o arquivo ser fechado continuar a execução do programa diferentemente de sbp.Popen()
            
            elif char == b'n':
                print('  | Ok, não se esqueça de checar o arquivo de configuração se algo não estiver funcionando corretamente :)')
                sys.exit(' >|')

        # Se der algum erro na criação do arquivo
        except Exception as e:
            print('  | Um erro ocorreu')
            print(' >|')
            sys.exit(e)
            


    # Caso não
    elif char == b'n':
        print('N')
        time.sleep(0.5)
        sys.exit('  | Um arquivo de configuração é necessario para proseguir.\n >|')

    else:
        char = str(char).upper().replace("B'", '').replace("'",'')
        exit(f"""{char}\n  | {char} Não é uma opção válida\n >|""")


# Wrappa tudo isso em uma função só, pra ficar mais bonitinho
def CheckCFG():
    # Faz com que 'config.json' existe e/ou trata os casos
    if os.path.isfile('config.json'):
        with open('config.json') as file:
            config = json.load(file)

            # Retorna config, assim você ja pode chamar a função instanciando-a
            return config
            
    # Chama a primeira função aqui, caso não exista
    else:
        createCFGfile()

