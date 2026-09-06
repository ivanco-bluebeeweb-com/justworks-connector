"""Panel UI for Justworks Connector following UI_INTERFACE_STANDARD.md and AUTH_AND_CREDENTIALS_STANDARD.md."""
from __future__ import annotations
from imperal_sdk import ui
from app import ext

def _settings_button() -> ui.UINode:
    return ui.Button(
        "App settings",
        variant="secondary",
        size="sm",
        icon="settings",
        on_click=ui.Call("__panel__justworks_settings")
    )

def _help_modal() -> ui.UINode:
    return ui.Modal(
        trigger=ui.Button("How do I connect Justworks?", variant="ghost", size="sm"),
        title="Connecting Justworks",
        children=[
            ui.Text(
                "1. Sign in to your Justworks organization at app.justworks.com.\n"
                "2. Navigate to Company Settings > Developer Integrations / API Access.\n"
                "3. Generate an API Access Token (Partner API / Members API).\n"
                "4. Paste your API token above and click Connect Justworks.",
                variant="body"
            )
        ]
    )

@ext.panel("justworks_sidebar", slot="left")
async def justworks_sidebar(ctx, **kwargs) -> ui.UINode:
    return ui.Stack(
        direction="v",
        gap=3,
        align="stretch",
        children=[
            ui.Text("Justworks", variant="heading"),
            ui.Text("Manage workforce, employees, payroll runs, departments, time-off and direct deposits via Justworks Partner API.", variant="caption"),
            ui.Divider(),
            ui.Form(
                submit_label="Connect Justworks",
                action=ui.Call("connect_justworks"),
                children=[
                    ui.Stack(
                        direction="v",
                        gap=2,
                        align="stretch",
                        children=[
                            ui.Text("Connection Label", variant="caption"),
                            ui.Input(
                                param_name="label",
                                placeholder="e.g. Acme Justworks",
                                value=""
                            ),
                            ui.Text("API Token", variant="caption"),
                            ui.Input(
                                param_name="api_token",
                                placeholder="Enter Justworks API Token",
                                value=""
                            ),
                            ui.Text("Base URL (Optional)", variant="caption"),
                            ui.Input(
                                param_name="base_url",
                                placeholder="https://public-api.justworks.com/v1",
                                value=""
                            )
                        ]
                    )
                ]
            ),
            ui.Divider(),
            _help_modal(),
            _settings_button()
        ]
    )
