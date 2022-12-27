from base.dash_utils import *

dash_directory = os.getcwd()
with open(os.path.join(dash_directory, 'assets', 'user_guide.md'), 'r') as f:
    interface_description = f.read()
project_description = {}
for i in (1, 2, 3, 4):
    with open(os.path.join(dash_directory, 'assets', f'project_{i}.md'), 'r') as f:
        project_description[i] = f.read()

app = DashProxy(__name__, suppress_callback_exceptions=True,
                transforms=[MultiplexerTransform()], title='RL Agent 2048', update_title=None,
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}])
application = app.server


app.layout = html.Div([
    dcc.Store(id='idx', storage_type='session'),
    dcc.Interval(id='vc', interval=dash_intervals['vc']),
    dcc.Interval(id='refresh_status', interval=dash_intervals['refresh']),
    dcc.Store(id='session_tags', storage_type='session'),
    dcc.Interval(id='initiate_logs', interval=dash_intervals['initiate_logs'], n_intervals=0),
    dcc.Store(id='log_file', data=None, storage_type='session'),
    dcc.Store(id='running_now', storage_type='session'),
    dcc.Download(id='download_file'),
    EventListener(id='keyboard'),
    dcc.Store(id='current_process', storage_type='session'),
    dcc.Store(id='agent_for_chart', storage_type='session'),
    dcc.Interval(id='update_interval', n_intervals=0, disabled=True),
    dcc.Interval(id='logs_interval', interval=dash_intervals['logs'], n_intervals=0),
    dbc.Modal(className='my-modal', id='user_page', backdrop='static', is_open=True, children=[
        dbc.ModalHeader(id='user_page_header', close_button=False, children=[
            html.Div('cost calculation results'),
            html.Button('Download', id='vert_table_down_btn'),
            html.Button('X', id='cost_modal_close')
        ]),
        dbc.ModalBody('Ola!', className='my-modal-body')])
    # dbc.Modal([
    #     dbc.ModalHeader([
    #         dbc.ButtonGroup([dbc.Button('User interface guide', id='guide_ui_button', color='info'),
    #                          dbc.Button('RL project description', id='guide_project_button')])]),
    #     dbc.ModalBody(id='guide_page_body')], id='guide_page', size='xl', centered=True, contentClassName='guide-page'),
    # dbc.Modal([
    #     while_loading('uploading', 25),
    #     dbc.ModalHeader('File Management'),
    #     dbc.ModalBody([
    #         dbc.DropdownMenu(id='choose_file_action', label='Action:',
    #                          children=[dbc.DropdownMenuItem(act_list[v], id=v, n_clicks=0) for v in act_list]),
    #         dbc.Select(id='choose_file', className='choose-file'),
    #         dbc.Button('action?', id='admin_go', n_clicks=0, className='admin-go'),
    #         dcc.Upload('Drag and Drop or Select Files', id='data_uploader', style={'display': 'none'},
    #                    className='upload-file')
    #     ], className='admin-page-body'),
    #     dbc.ModalFooter([
    #         html.Div(id='admin_notification'),
    #         dbc.Button('CLOSE', id='close_admin', n_clicks=0)
    #     ])
    # ], id='admin_page', size='lg', centered=True, contentClassName='admin-page'),
    # dbc.Modal([
    #     while_loading('fill_loading', 125),
    #     while_loading('loading', 125),
    #     dbc.ModalHeader('Enter/adjust/confirm parameters for an Agent'),
    #     dbc.ModalBody([params_line(e) for e in params_list], className='params-page-body'),
    #     dbc.ModalFooter([
    #         dbc.Button('TRAIN', id='start_training', n_clicks=0, className='start-training'),
    #         html.Div(id='params_notification'),
    #         dbc.Button('CLOSE', id='close_params', n_clicks=0)
    #     ])
    # ], id='params_page', size='lg', centered=True, contentClassName='params-page'),
    # dbc.Modal([
    #     while_loading('chart_loading', 0),
    #     dbc.ModalHeader(id='chart_header'),
    #     dbc.ModalBody(id='chart'),
    #     dbc.ModalFooter(dbc.Button('CLOSE', id='close_chart', n_clicks=0))
    # ], id='chart_page', size='xl', centered=True, contentClassName='chart-page'),
    # dbc.Row(html.H4(['Reinforcement Learning 2048 Agent ',
    #                  dcc.Link('\u00A9abachurin', href='https://www.abachurin.com', target='blank')],
    #                 className='card-header my-header')),
    # dbc.Row([
    #     dbc.Col(dbc.Card([
    #         html.H6('Choose:', id='mode_text', className='mode-text'),
    #         dbc.DropdownMenu(id='mode_menu', label='MODE ?', color='success', className='mode-choose', disabled=True,
    #                          children=[dbc.DropdownMenuItem(mode_list[v][0], id=v, n_clicks=0, disabled=False)
    #                                    for v in mode_list]),
    #         dbc.Button(id='chart_button', className='chart-button', style={'display': 'none'}),
    #         dbc.InputGroup([
    #             dbc.InputGroupText('Game:', className='input-text'),
    #             dbc.Select(id='choose_for_replay', className='input-field'),
    #             html.A(dbc.Button('REPLAY', id='replay_game_button', disabled=True, className='replay-game'),
    #                    href='#gauge_group'),
    #             ], id='input_group_game', style={'display': 'none'}, className='my-input-group',
    #         ),
    #         dbc.InputGroup([
    #             while_loading('test_loading', 225),
    #             while_loading('agent_play_loading', 225),
    #             dbc.InputGroupText('Agent:', className='input-text'),
    #             dbc.Select(id='choose_stored_agent', className='input-field'),
    #             html.Div([
    #                 dbc.InputGroupText('depth:', className='lf-cell lf-text lf-depth'),
    #                 dbc.Input(id='choose_depth', type='number', min=0, max=4, value=0,
    #                           className='lf-cell lf-field lf-depth'),
    #                 dbc.InputGroupText('width:', className='lf-cell lf-text lf-width'),
    #                 dbc.Input(id='choose_width', type='number', min=1, max=4, value=1,
    #                           className='lf-cell lf-field lf-width'),
    #                 dbc.InputGroupText('empty:', className='lf-cell lf-text lf-empty'),
    #                 dbc.Input(id='choose_since_empty', type='number', min=0, max=8, value=6,
    #                           className='lf-cell lf-field lf-empty'),
    #             ], className='lf-params'),
    #             dbc.Button('LAUNCH!', id='replay_agent_button', disabled=True, className='launch-game'),
    #             html.Div([
    #                 dbc.InputGroupText('N:', className='num-eps-text'),
    #                 dbc.Input(id='choose_num_eps', type='number', min=1, value=100, step=1, className='num-eps-field')
    #                 ], id='num_eps', style={'display': 'none'}, className='num-eps')
    #             ], id='input_group_agent', style={'display': 'none'}, className='my-input-group',
    #         ),
    #         dbc.InputGroup([
    #             dbc.InputGroupText('Agent:', className='input-text'),
    #             dbc.Select(id='choose_train_agent', className='input-field'),
    #             dbc.InputGroupText('Config:', className='input-text config-text'),
    #             dbc.Select(id='choose_config', disabled=True, className='input-field config-input'),
    #             dbc.Button('Confirm parameters', id='go_to_params', disabled=True, className='go-to-params'),
    #             ], id='input_group_train', style={'display': 'none'}, className='my-input-group',
    #         ),
    #         html.Div([
    #                 html.H6('Logs', className='logs-header card-header'),
    #                 dbc.Button('Stop', id='stop_agent', n_clicks=0, className='logs-button stop-agent',
    #                            style={'display': 'none'}),
    #                 dbc.Button('Download', id='download_logs', n_clicks=0, className='logs-button logs-download'),
    #                 dbc.Button('Clear', id='clear_logs', n_clicks=0, className='logs-button logs-clear'),
    #                 html.Div(id='logs_display', className='logs-display'),
    #                 html.Div(id='log_footer', className='card-footer log-footer')
    #             ], className='logs-window'),
    #         ], className='log-box'),
    #     ),
    #     dbc.Col([
    #         dbc.Card([
    #             dbc.Toast('Use buttons below or keyboard!\n'
    #                       'When two equal tiles collide, they combine to give you one '
    #                       'greater tile that displays their sum. The more you do this, obviously, the higher the '
    #                       'tiles get and the more crowded the board becomes. Your objective is to reach highest '
    #                       'possible score before the board fills up', header='Game instructions',
    #                       headerClassName='inst-header', id='play_instructions', dismissable=True, is_open=False),
    #             dbc.CardBody(id='game_card'),
    #             html.Div([
    #                 daq.Gauge(id='gauge', className='gauge',
    #                           color={"gradient": True, "ranges": {"blue": [0, 6], "yellow": [6, 8], "red": [8, 10]}}),
    #                 html.H6('DELAY', className='speed-header'),
    #                 dcc.Slider(id='gauge-slider', min=0, max=10, value=3, marks={v: str(v) for v in range(11)},
    #                            step=0.1, className='slider'),
    #                 html.Div([
    #                     dbc.Button('PAUSE', id='pause_game', n_clicks=0, className='one-button pause-button'),
    #                     dbc.Button('RESUME', id='resume_game', n_clicks=0, className='one-button resume-button'),
    #                 ], className='button-line')
    #             ], id='gauge_group', className='gauge-group'),
    #             html.Div([
    #                 dbc.Button('\u2190', id='move_0', className='move-button move-left'),
    #                 dbc.Button('\u2191', id='move_1', className='move-button move-up'),
    #                 dbc.Button('\u2192', id='move_2', className='move-button move-right'),
    #                 dbc.Button('\u2193', id='move_3', className='move-button move-down'),
    #                 dbc.Button('RESTART', id='restart_play', className='restart-play'),
    #             ], id='play-yourself-group', className='gauge-group', style={'display': 'none'}),
    #         ], className='log-box align-items-center'),
    #     ])
    # ])
])


# Project description callbacks
@app.callback(
    Output('guide_page', 'is_open'),
    Input('description_button', 'n_clicks'),
)
def toggle_guide_page(n):
    return bool(n)


@app.callback(
    Output('guide_page_body', 'children'),
    Input('guide_project_button', 'n_clicks'),
)
def show_project_description(n):
    if n:
        return [
            dcc.Markdown(project_description[1], link_target='_blanc', className='md_content'),
            html.Img(src=app.get_asset_url('score_chart_2_tile.png')),
            dcc.Markdown(project_description[2], link_target='_blanc', className='md_content'),
            html.Img(src=app.get_asset_url('score_chart_3_tile.png')),
            dcc.Markdown(project_description[3], link_target='_blanc', className='md_content'),
            html.Img(src=app.get_asset_url('score_chart_5_tile.png')),
            dcc.Markdown(project_description[4], link_target='_blanc', className='md_content')
        ]
    else:
        raise PreventUpdate


# Project description callbacks
@app.callback(
    Output('guide_page_body', 'children'),
    Input('guide_ui_button', 'n_clicks'),
)
def show_ui_description(n):
    return dcc.Markdown(interface_description, dedent=False, link_target='_blanc', className='md_content')


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


for mod in modals_to_drag:
    app.clientside_callback(
        ClientsideFunction(namespace='clientside', function_name='make_draggable'),
        Output(mod, 'className'),
        Input(mod, 'is_open'), State(mod, 'id')
    )


if __name__ == '__main__':

    if LOCAL == 'local':
        app.run_server(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)), debug=True, use_reloader=False)
    else:
        application.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)), debug=False, use_reloader=False)

