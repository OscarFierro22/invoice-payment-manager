import flet as ft

from views.empresa_view import mostrar_registro_empresa
from views.factura_view import mostrar_registro_factura
from views.menu_view import mostrar_menu


def main(page: ft.Page):

    # ---------------------------------------------------------
    # CONFIGURACIÓN
    # ---------------------------------------------------------

    page.title = (
        "Control de Facturas - ELECTROPART SA"
    )

    page.padding = 25

    # ---------------------------------------------------------
    # NAVEGACIÓN
    # ---------------------------------------------------------

    def abrir_menu():

        mostrar_menu(
            page=page,
            abrir_factura=abrir_factura,
            abrir_empresa=abrir_empresa,
        )

    def abrir_factura():

        mostrar_registro_factura(
            page=page,
            volver_menu=abrir_menu,
        )

    def abrir_empresa():

        mostrar_registro_empresa(
            page=page,
            volver_menu=abrir_menu,
        )

    # ---------------------------------------------------------
    # INICIO
    # ---------------------------------------------------------

    abrir_menu()


ft.run(main)