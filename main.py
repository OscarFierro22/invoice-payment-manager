import flet as ft


def main(page: ft.Page):
    # Configuración general de la aplicación
    page.title = "Control de Facturas - ELECTROPART SA"
    page.padding = 50

    
    status_text = ft.Text(
        "Seleccione una opción del menú.",
        size=20,
    )

    # ---------------------------------------------------------
    # EVENTOS DE LOS BOTONES
    # ---------------------------------------------------------

    def registrar_factura(e):
        status_text.value = "Seleccionaste: Registrar factura"
        page.update()

    def registrar_pago(e):
        status_text.value = "Seleccionaste: Registrar pago"
        page.update()

    def buscar(e):
        status_text.value = "Seleccionaste: Buscar"
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
                ),
                ft.Text(
                    "Control de Facturas y Pagos",
                    size=16,
                ),
            ],
            spacing=5,
        ),
    )

    # ---------------------------------------------------------
    # MENÚ PRINCIPAL
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
    # AGREGAR TODO A LA PÁGINA
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


ft.run(main)