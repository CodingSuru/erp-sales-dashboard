# pages/config.py
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, callback, ctx
import config_store
import oracledb
import os
from sqlalchemy import create_engine, text

# Global variable to track if thick mode is initialized
_thick_mode_initialized = False

def ensure_thick_mode():
    """Ensure Oracle thick mode is properly initialized"""
    global _thick_mode_initialized
    
    if _thick_mode_initialized:
        return True
    
    # Common Oracle Instant Client installation paths
    ORACLE_CLIENT_PATHS = [
        "C:\\oracle\\instantclient_23_8",
        "C:\\oracle\\instantclient_21_3", 
        "C:\\oracle\\instantclient_19_3",
        "C:\\oracle\\instantclient_12_2",
        "C:\\instantclient_23_8",
        "C:\\instantclient_21_3",
        "C:\\instantclient_19_3",
        "C:\\instantclient_12_2",
        "/opt/oracle/instantclient_23_8",
        "/opt/oracle/instantclient_21_3",
        "/usr/lib/oracle/23/client64/lib",
        "/usr/lib/oracle/21/client64/lib",
        "/usr/lib/oracle/19.3/client64/lib"
    ]
    
    for client_path in ORACLE_CLIENT_PATHS:
        try:
            if os.path.exists(client_path):
                print(f"Attempting to initialize Oracle thick mode with: {client_path}")
                oracledb.init_oracle_client(lib_dir=client_path)
                print(f"✅ Oracle thick mode initialized successfully with: {client_path}")
                _thick_mode_initialized = True
                return True
        except Exception as e:
            print(f"Failed to initialize Oracle client at {client_path}: {e}")
            continue
    
    print("⚠ Warning: Could not initialize Oracle thick mode. Thick mode requires Oracle Instant Client.")
    return False

# Try to initialize thick mode when module loads
thick_mode_available = ensure_thick_mode()

# Register this as the /config page
dash.register_page(__name__, path="/config", name="Database Configuration")

layout = html.Div([
    # Full screen background with gradient
    html.Div([
        html.Div([
            # Header Section
            html.Div([
                html.H1("ERP Database Configuration", 
                       className="text-white text-center mb-1",
                       style={'fontSize': '3rem', 'fontWeight': 'bold'}),
                html.P("Configure your Oracle database connection or upload CSV data",
                      className="text-white text-center mb-4",
                      style={'fontSize': '1.2rem', 'opacity': '0.9'})
            ], className="mb-5"),
            
            # Tab Selection
            dbc.Tabs([
                # Oracle Database Tab
                dbc.Tab([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H4("Database Connection Setup", className="mb-0 text-center"),
                            html.Hr(),
                            dbc.Alert([
                                html.I(className="fas fa-info-circle me-2"),
                                "Oracle Connection Mode: " + ("✅ Thick Mode Enabled" if thick_mode_available else "⚠️ Thin Mode (Limited Compatibility)")
                            ], color="success" if thick_mode_available else "warning", className="mb-0")
                        ]),
                        
                        dbc.CardBody([
                            dbc.Form([
                                dbc.Row([
                                    dbc.Col([
                                        html.Label("Database Server", className="form-label fw-bold"),
                                        dcc.Input(
                                            id="server-input",
                                            type="text",
                                            placeholder="192.168.1.206",
                                            className="form-control form-control-lg",
                                            style={'borderRadius': '10px'}
                                        )
                                    ], md=6),
                                    dbc.Col([
                                        html.Label("Port", className="form-label fw-bold"),
                                        dcc.Input(
                                            id="port-input",
                                            type="text",
                                            placeholder="1521",
                                            className="form-control form-control-lg",
                                            style={'borderRadius': '10px'}
                                        )
                                    ], md=6)
                                ], className="mb-4"),
                                
                                dbc.Row([
                                    dbc.Col([
                                        html.Label("Service Name", className="form-label fw-bold"),
                                        dcc.Input(
                                            id="service-input",
                                            type="text",
                                            placeholder="ORCL",
                                            className="form-control form-control-lg",
                                            style={'borderRadius': '10px'}
                                        )
                                    ], md=12)
                                ], className="mb-4"),
                                
                                dbc.Row([
                                    dbc.Col([
                                        html.Label("Username", className="form-label fw-bold"),
                                        dcc.Input(
                                            id="username-input",
                                            type="text",
                                            placeholder="Enter username",
                                            className="form-control form-control-lg",
                                            style={'borderRadius': '10px'}
                                        )
                                    ], md=6),
                                    dbc.Col([
                                        html.Label("Password", className="form-label fw-bold"),
                                        dcc.Input(
                                            id="password-input",
                                            type="password",
                                            placeholder="Enter password",
                                            className="form-control form-control-lg",
                                            style={'borderRadius': '10px'}
                                        )
                                    ], md=6)
                                ], className="mb-4"),
                                
                                html.Div([
                                    dbc.Button(
                                        [html.I(className="fas fa-plug me-2"), "Test Connection"],
                                        id="test-connection-btn",
                                        color="info",
                                        size="lg",
                                        className="me-3",
                                        style={'borderRadius': '25px', 'paddingLeft': '30px', 'paddingRight': '30px'}
                                    ),
                                    dbc.Button(
                                        [html.I(className="fas fa-arrow-right me-2"), "Submit & Proceed"],
                                        id="submit-proceed-btn",
                                        color="success",
                                        size="lg",
                                        disabled=True,
                                        style={'borderRadius': '25px', 'paddingLeft': '30px', 'paddingRight': '30px'}
                                    )
                                ], className="text-center mb-4"),
                                
                                html.Div(id="connection-status", className="mt-3")
                            ])
                        ])
                    ], style={'borderRadius': '15px', 'border': 'none', 'boxShadow': '0 10px 30px rgba(0,0,0,0.1)'})
                ], label="Oracle Database", tab_id="oracle-tab"),
                
                # CSV Upload Tab
                dbc.Tab([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H4("Upload CSV Data", className="mb-0 text-center"),
                            html.Hr(),
                            dbc.Alert([
                                html.I(className="fas fa-info-circle me-2"),
                                "Upload your sales data CSV file directly"
                            ], color="info", className="mb-0")
                        ]),
                        
                        dbc.CardBody([
                            dcc.Upload(
                                id='upload-csv',
                                children=html.Div([
                                    html.I(className="fas fa-cloud-upload-alt", style={'fontSize': '2.5rem', 'color': '#667eea'}),
                                    html.Br(),
                                    html.H6('Drag and Drop or Click to Select CSV File', style={'marginTop': '15px', 'marginBottom': '5px'}),
                                    html.P('Supported format: CSV', className="text-muted small")
                                ], style={'paddingTop': '30px'}),
                                style={
                                    'width': '100%',
                                    'height': '150px',
                                    'borderWidth': '2px',
                                    'borderStyle': 'dashed',
                                    'borderRadius': '10px',
                                    'textAlign': 'center',
                                    'cursor': 'pointer',
                                    'marginBottom': '20px'
                                },
                                multiple=False
                            ),
                            
                            html.Div(id="csv-upload-status", className="mb-3"),
                            
                            html.Div([
                                dbc.Button(
                                    [html.I(className="fas fa-arrow-right me-2"), "Proceed to Dashboard"],
                                    id="csv-proceed-btn",
                                    color="success",
                                    size="lg",
                                    disabled=True,
                                    style={'borderRadius': '25px', 'paddingLeft': '30px', 'paddingRight': '30px'}
                                )
                            ], className="text-center")
                        ])
                    ], style={'borderRadius': '15px', 'border': 'none', 'boxShadow': '0 10px 30px rgba(0,0,0,0.1)'})
                ], label="Upload CSV", tab_id="csv-tab")
            ], id="config-tabs", active_tab="csv-tab", className="mb-4")
            
        ], style={'maxWidth': '800px', 'margin': '0 auto', 'padding': '20px'})
    ], style={
        'minHeight': '100vh',
        'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'padding': '50px 20px'
    }),
    
    dcc.Location(id='csv-redirect', refresh=True)
])

@callback(
    [Output("csv-upload-status", "children"),
     Output("csv-proceed-btn", "disabled")],
    Input("upload-csv", "contents"),
    State("upload-csv", "filename"),
    prevent_initial_call=True
)
def handle_csv_upload(contents, filename):
    if contents is None:
        return "", True
    
    try:
        import base64
        import io
        import pandas as pd
        
        # Decode the uploaded file
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        # Read CSV
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        
        if df.empty:
            return dbc.Alert([
                html.I(className="fas fa-exclamation-triangle me-2"),
                "The uploaded CSV file is empty"
            ], color="warning"), True
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Save to data/erp_sales_data.csv
        output_path = os.path.join("data", "erp_sales_data.csv")
        df.to_csv(output_path, index=False)
        
        # Store config to indicate data is loaded
        config_store.db_config = {
            'source': 'csv',
            'filename': filename,
            'rows': len(df),
            'columns': len(df.columns)
        }
        
        # Success message
        return dbc.Alert([
            html.I(className="fas fa-check-circle me-2"),
            f"✅ File '{filename}' uploaded successfully! ({len(df)} rows, {len(df.columns)} columns)"
        ], color="success"), False
        
    except Exception as e:
        return dbc.Alert([
            html.I(className="fas fa-times-circle me-2"),
            f"Error processing CSV: {str(e)}"
        ], color="danger"), True

@callback(
    Output("csv-redirect", "href"),
    Input("csv-proceed-btn", "n_clicks"),
    prevent_initial_call=True
)
def proceed_from_csv(n_clicks):
    if n_clicks:
        return "/sales"
    return ""

@callback(
    [Output("connection-status", "children"),
     Output("submit-proceed-btn", "disabled")],
    Input("test-connection-btn", "n_clicks"),
    Input("submit-proceed-btn", "n_clicks"),
    State("server-input", "value"),
    State("port-input", "value"),
    State("service-input", "value"),
    State("username-input", "value"),
    State("password-input", "value"),
    prevent_initial_call=True
)
def handle_connection_actions(test_clicks, submit_clicks, server, port, service, username, password):
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if not all([server, port, service, username, password]):
        return dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            "Please fill in all required fields"
        ], color="warning"), True
    
    conn_str = f'oracle+oracledb://{username}:{password}@{server}:{port}/{service}'
    
    if triggered_id == "test-connection-btn":
        try:
            engine = create_engine(conn_str, pool_pre_ping=True, pool_recycle=3600)
            
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1 FROM DUAL"))
                result.fetchone()
            
            engine.dispose()
            
            mode_info = "Thick Mode" if _thick_mode_initialized else "Thin Mode"
            return dbc.Alert([
                html.I(className="fas fa-check-circle me-2"),
                f"Connection successful using {mode_info}! You can now proceed."
            ], color="success"), False
            
        except Exception as e:
            error_msg = str(e)
            if "DPY-3010" in error_msg:
                return dbc.Alert([
                    html.H5([html.I(className="fas fa-times-circle me-2"), "Oracle Version Not Supported"], className="mb-3"),
                    html.P("Your Oracle database version requires thick mode with Oracle Instant Client."),
                    html.Hr(),
                    html.P("Solutions:", className="mb-2 fw-bold"),
                    dbc.ListGroup([
                        dbc.ListGroupItem("Install Oracle Instant Client"),
                        dbc.ListGroupItem("Ask your DBA to upgrade Oracle Database to version 12.1+"),
                        dbc.ListGroupItem("Use CSV upload option instead")
                    ], flush=True),
                    html.Hr(),
                    html.Small(f"Technical details: {error_msg}", className="text-muted")
                ], color="danger"), True
            else:
                return dbc.Alert([
                    html.I(className="fas fa-times-circle me-2"),
                    f"Connection failed: {error_msg}"
                ], color="danger"), True
    
    elif triggered_id == "submit-proceed-btn":
        try:
            engine = create_engine(conn_str, pool_pre_ping=True, pool_recycle=3600)
            
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1 FROM DUAL"))
                result.fetchone()
            
            config_store.db_config = {
                'server': server,
                'port': port,
                'service': service,
                'username': username,
                'password': password,
                'conn_str': conn_str,
                'engine': engine,
                'thick_mode': _thick_mode_initialized
            }
            
            return dcc.Location(pathname="/data-fetching", id="redirect-to-data-fetching"), True
            
        except Exception as e:
            error_msg = str(e)
            return dbc.Alert([
                html.I(className="fas fa-times-circle me-2"),
                f"Configuration failed: {error_msg}"
            ], color="danger"), True
    
    return "", True
