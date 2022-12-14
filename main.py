from base.dash_utils import *


LOCAL = os.environ.get('S3_URL', 'local')
BACK_URL = os.environ.get('ROOT_URL', 'http://host.docker.internal:3000')


app = DashProxy(__name__, suppress_callback_exceptions=True,
                transforms=[MultiplexerTransform()], title='RL Agent 2048', update_title=None,
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}])
application = app.server

app.layout = html.Div([
    dbc.Input(placeholder='Input number: ', id='input', type='number'),
    html.Div(id='output'),
    html.Br(),
    dbc.Button('List of S3 files = ', id='files', size='large'),
    html.Br(),
    dbc.Textarea(id='list', style={'width': '500px', 'height': '200px', 'border': '2px solid'})
])


@app.callback(
    Output('output', 'children'),
    Input('input', 'value')
)
def get_square(n):
    payload = {}
    headers = {}
    url = f'{BACK_URL}/test/{n}'
    response = requests.request('GET', url, headers=headers, data=payload)
    return json.loads(response.text).get('value', 'None')


@app.callback(
    Output('list', 'value'),
    Input('files', 'n_clicks')
)
def get_square(n):
    if n:
        payload = {}
        headers = {}
        url = f'{BACK_URL}/files'
        response = requests.request('GET', url, headers=headers, data=payload)
        return json.loads(response.text).get('files', 'None')
    else:
        raise PreventUpdate


if __name__ == '__main__':

    if LOCAL == 'local':
        app.run_server(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True, use_reloader=False)
    else:
        application.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=False, use_reloader=False)
