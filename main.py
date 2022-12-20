from base.dash_utils import *


app = DashProxy(__name__, suppress_callback_exceptions=True,
                transforms=[MultiplexerTransform()], title='RL Agent 2048', update_title=None,
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}])
application = app.server

app.layout = html.Div([
    dbc.Button('List of S3 files = ', id='get_users', size='large'),
    html.Br(),
    dbc.Textarea(id='list', style={'width': '500px', 'height': '200px', 'border': '2px solid'})
])


@app.callback(
    Output('list', 'value'),
    Input('get_users', 'n_clicks')
)
def get_square(n):
    if n:
        payload = {}
        headers = {}
        url = f'{ROOT_URL}/users/list'
        response = requests.request('GET', url, headers=headers, data=payload)
        if response.status_code != 200:
            return 'Unable to connect'
        return json.loads(response.text).get('user_list', 'None')
    else:
        raise PreventUpdate


if __name__ == '__main__':

    if LOCAL == 'local':
        app.run_server(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)), debug=True, use_reloader=False)
    else:
        application.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)), debug=False, use_reloader=False)

