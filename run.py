import flet as ft
import requests
import json


base_url: str = 'http://192.168.104.179:8080/api'


def main(page: ft.Page):
    session = requests.session()
    page.theme_mode = 'light'

    def logout(e):
        if e.data == 'close':
            r = session.get(f'{base_url}/logoff')
            print(f'Logoff efetuado: {r.status_code}')
            page.window_destroy()
    
    page.window_prevent_close = True
    page.on_window_event = logout
    
    def login(e):
        if not input_username.value:
            input_username.error_text = 'Informe o usuário'
            page.update()
            return
        if not input_password.value:
            input_password.error_text = 'Informe a senha'
            page.update()
            return

        headers: dict = {
            'Content-Type': 'application/json'
        }

        payload: dict = {
            "userName": input_username.value,
            "password": input_password.value,
            "rememberMe": True,
            "accountId": 0
        }

        payload = json.dumps(payload)

        r = session.put(
            f'{base_url}/login',
            headers=headers,
            data=payload
        )

        if r.status_code == 200:
            page.clean()

            portas = {}

            def get_porta(name: str):
                return portas.get(name, None)

            def abrir_porta(e):
                if not select_portas.value:
                    select_portas.error_text = 'Selecione uma porta para abrir'
                    return
                
                porta = get_porta(select_portas.value)
                if porta:
                    accountId = porta['accountId']
                    serverId = porta['serverId']
                    doorId = porta['doorId']

                    r = session.put(
                        f'{base_url}/accounts/{accountId}/servers/{serverId}/doors/{doorId}',
                        data={
                            "integrationId": 0,
                            "personId": 0,
                            "visitorId": 0,
                            "schedulingId": 0
                        }
                    )

                    print(r.content)

                    dlg = ft.AlertDialog(title=ft.Text(f'Porta aberta: {r.status_code}'))
                    page.dialog = dlg
                    dlg.open = True
                    page.update()
            
            r = session.get(f'{base_url}/doors')

            select_portas = ft.Dropdown(width=300)
            options_portas = []
            for porta in r.json()['doors']:
                options_portas.append(ft.dropdown.Option(porta['name']))
                portas[porta['name']] = porta
            
            select_portas.options = options_portas
            button_open = ft.ElevatedButton('Abrir porta', on_click=abrir_porta)

            page.add(select_portas)
            page.add(button_open)
    
    page.title = 'Open Door'
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    input_username: ft.TextField = ft.TextField(label='Usuário')
    input_password: ft.TextField = ft.TextField(label='Senha', password=True)
    button_submit: ft.ElevatedButton = ft.ElevatedButton('Logar', on_click=login)

    column: ft.Column = ft.Column(
        controls=[
            input_username,
            input_password,
            button_submit
        ]
    )

    page.add(column)


ft.app(target=main)