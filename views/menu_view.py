import flet as ft


def mostrar_menu(
    page: ft.Page,
    abrir_factura,
    abrir_empresa,
    abrir_productos,
):
    """
    Construye y muestra el menú principal.
    """

    page.clean()

    # Algunas pantallas utilizan scroll.
    # Al regresar al menú lo dejamos en su estado normal.
    page.scroll = None

    # ---------------------------------------------------------
    # MENSAJE DE ESTADO
    # ---------------------------------------------------------

    status_text = ft.Text(
        "Seleccione una opción del menú.",
        size=16,
    )

    # ---------------------------------------------------------
    # EVENTOS
    # ---------------------------------------------------------

    def registrar_factura(e):

        abrir_factura()

    def registrar_empresa(e):

        abrir_empresa()

    def gestionar_productos(e):

        abrir_productos()

    def registrar_pago(e):

        status_text.value = (
            "El módulo Registrar pago "
            "se implementará próximamente."
        )

        page.update()

    def buscar(e):

        status_text.value = (
            "El módulo Buscar "
            "se implementará próximamente."
        )

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
                    "ELECTROPART SA",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
                ft.Text(
                    "Control de Compras, Facturación y Pagos",
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

            # -------------------------------------------------
            # FACTURAS
            # -------------------------------------------------

            ft.Button(
                content="Registrar factura",
                height=70,
                on_click=registrar_factura,
                col={
                    "xs": 12,
                    "sm": 6,
                    "lg": 3,
                },
            ),

            # -------------------------------------------------
            # PAGOS
            # -------------------------------------------------

            ft.Button(
                content="Registrar pago",
                height=70,
                on_click=registrar_pago,
                col={
                    "xs": 12,
                    "sm": 6,
                    "lg": 3,
                },
            ),

            # -------------------------------------------------
            # BÚSQUEDA
            # -------------------------------------------------

            ft.Button(
                content="Buscar",
                height=70,
                on_click=buscar,
                col={
                    "xs": 12,
                    "sm": 6,
                    "lg": 3,
                },
            ),

            # -------------------------------------------------
            # EMPRESAS
            # -------------------------------------------------

            ft.Button(
                content="Empresas",
                height=70,
                on_click=registrar_empresa,
                col={
                    "xs": 12,
                    "sm": 6,
                    "lg": 3,
                },
            ),

            # -------------------------------------------------
            # PRODUCTOS
            # -------------------------------------------------

            ft.Button(
                content="Productos",
                height=70,
                on_click=gestionar_productos,
                col={
                    "xs": 12,
                    "sm": 6,
                    "lg": 3,
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