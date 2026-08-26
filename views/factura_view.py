import flet as ft


def mostrar_registro_factura(page: ft.Page, volver_menu):
    """
    Muestra el formulario para registrar una factura.

    En esta primera versión el formulario todavía
    no guarda información en Excel.
    """

    page.clean()

    # ---------------------------------------------------------
    # CAMPOS DEL FORMULARIO
    # ---------------------------------------------------------

    empresa_field = ft.TextField(
        label="Empresa / Emisor",
    )

    ruc_field = ft.TextField(
        label="RUC",
    )

    numero_factura_field = ft.TextField(
        label="Número de factura",
    )

    fecha_emision_field = ft.TextField(
        label="Fecha de emisión",
        hint_text="dd/mm/aaaa",
    )

    total_field = ft.TextField(
        label="Valor total",
        hint_text="0.00",
    )

    mensaje = ft.Text(
        "",
        size=14,
    )

    # ---------------------------------------------------------
    # EVENTOS
    # ---------------------------------------------------------

    def guardar_factura(e):
        mensaje.value = (
            "Formulario recibido. "
            "En el siguiente módulo aprenderemos a guardar estos datos."
        )
        page.update()

    def regresar(e):
        volver_menu()

    # ---------------------------------------------------------
    # ENCABEZADO
    # ---------------------------------------------------------

    encabezado = ft.Row(
        controls=[
            ft.Button(
                content="← Volver",
                on_click=regresar,
            ),
            ft.Text(
                "Registrar factura",
                size=24,
                weight=ft.FontWeight.BOLD,
            ),
        ],
        spacing=15,
    )

    # ---------------------------------------------------------
    # FORMULARIO RESPONSIVE
    # ---------------------------------------------------------

    formulario = ft.ResponsiveRow(
        spacing=15,
        run_spacing=15,
        controls=[
            ft.Container(
                content=empresa_field,
                col={
                    "xs": 12,
                    "md": 6,
                },
            ),
            ft.Container(
                content=ruc_field,
                col={
                    "xs": 12,
                    "md": 6,
                },
            ),
            ft.Container(
                content=numero_factura_field,
                col={
                    "xs": 12,
                    "md": 6,
                },
            ),
            ft.Container(
                content=fecha_emision_field,
                col={
                    "xs": 12,
                    "md": 6,
                },
            ),
            ft.Container(
                content=total_field,
                col={
                    "xs": 12,
                    "md": 6,
                },
            ),
        ],
    )

    # ---------------------------------------------------------
    # BOTONES
    # ---------------------------------------------------------

    acciones = ft.Row(
        controls=[
            ft.Button(
                content="Guardar factura",
                on_click=guardar_factura,
            ),
        ],
    )

    # ---------------------------------------------------------
    # MOSTRAR PANTALLA
    # ---------------------------------------------------------

    page.add(
        ft.SafeArea(
            content=ft.Column(
                controls=[
                    encabezado,
                    ft.Divider(),
                    formulario,
                    acciones,
                    mensaje,
                ],
                spacing=20,
            )
        )
    )