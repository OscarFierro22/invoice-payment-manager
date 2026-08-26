import flet as ft


def mostrar_menu(page: ft.Page, abrir_factura):
    """
    Parameters
    ----------
    page:
        Página principal proporcionada por Flet.

    abrir_factura:
        Función que se ejecutará cuando el usuario
        presione el botón "Registrar factura".
    """

    # Eliminamos los controles de la pantalla anterior.
    page.clean()

    # Mensaje inferior del menú.
    status_text = ft.Text(
        "Seleccione una opción del menú.",
        size=16,
    )

    # ---------------------------------------------------------
    # EVENTOS
    # ---------------------------------------------------------

    def registrar_factura(e):
        abrir_factura()

    def registrar_pago(e):
        status_text.value = "El módulo Registrar pago se implementará próximamente."
        page.update()

    def buscar(e):
        status_text.value = "El módulo Buscar se implementará próximamente."
        page.update()

    # ---------------------------------------------------------
    # ENCABEZADO
    # ---------------------------------------------------------

    encabezado = ft.Container(
        padding=20,
        border_radius=12,
        bgcolor=ft.Colors.BLACK,
        content=ft.Column(
            controls=[
                ft.Text(
                    "******* EMPRESA *******",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
                ft.Text(
                    "Control de Facturas y Pagos",
                    size=16,
                    color=ft.Colors.WHITE,
                ),
            ],
            spacing=5,
        ),
    )

    # ---------------------------------------------------------
    # MENÚ
    # ---------------------------------------------------------

    menu = ft.ResponsiveRow(
        spacing=15,
        run_spacing=15,
        controls=[
            ft.Button(
                content="Registrar factura",
                height=70,
                on_click=registrar_factura,
                col={
                    "xs": 12,
                    "md": 4,
                },
            ),
            ft.Button(
                content="Registrar pago",
                height=70,
                on_click=registrar_pago,
                col={
                    "xs": 12,
                    "md": 4,
                },
            ),
            ft.Button(
                content="Buscar",
                height=70,
                on_click=buscar,
                col={
                    "xs": 12,
                    "md": 4,
                },
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
                    ft.Text(
                        "Menú principal",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                    ),
                    menu,
                    status_text,
                ],
                spacing=20,
            )
        )
    )