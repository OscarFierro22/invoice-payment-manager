import flet as ft

from views.menu_view import mostrar_menu
from views.factura_view import mostrar_registro_factura


def main(page: ft.Page):
    # ---------------------------------------------------------
    # CONFIGURACIÓN GENERAL
    # ---------------------------------------------------------

    page.title = "Control de Facturas - ELECTROPART SA"
    page.padding = 25

    # ---------------------------------------------------------
    # NAVEGACIÓN
    # ---------------------------------------------------------

    def abrir_menu():
        mostrar_menu(
            page=page,
            abrir_factura=abrir_factura,
        )

    def abrir_factura():
        mostrar_registro_factura(
            page=page,
            volver_menu=abrir_menu,
        )

    # ---------------------------------------------------------
    # PANTALLA INICIAL
    # ---------------------------------------------------------

    abrir_menu()


ft.run(main)