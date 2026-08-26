import flet as ft

from services.empresa_service import (
    listar_empresas,
    registrar_empresa,
)

from utils.validators import (
    validar_ruc,
    validar_texto_obligatorio,
)


def mostrar_registro_empresa(
    page: ft.Page,
    volver_menu,
):
    """
    Permite registrar empresas/clientes y consultar
    las empresas existentes.
    """

    page.clean()

    # ---------------------------------------------------------
    # CAMPOS
    # ---------------------------------------------------------

    nombre_field = ft.TextField(
        label="Nombre de empresa / cliente",
        hint_text="Ej: Hotel Río Amazonas",
    )

    ruc_field = ft.TextField(
        label="RUC",
        max_length=13,
    )

    nombre_error = ft.Text(
        "",
        color=ft.Colors.RED,
        visible=False,
    )

    ruc_error = ft.Text(
        "",
        color=ft.Colors.RED,
        visible=False,
    )

    mensaje = ft.Text(
        "",
        size=14,
    )

    lista_empresas = ft.Column(
        spacing=10,
    )

    # ---------------------------------------------------------
    # MOSTRAR EMPRESAS EXISTENTES
    # ---------------------------------------------------------

    def refrescar_empresas():

        lista_empresas.controls.clear()

        empresas = listar_empresas()

        if not empresas:

            lista_empresas.controls.append(
                ft.Text(
                    "Todavía no existen empresas registradas."
                )
            )

            return

        for empresa in empresas:

            lista_empresas.controls.append(
                ft.Container(
                    padding=10,
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                empresa["nombre"],
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                f'RUC: {empresa["ruc"]}'
                            ),
                        ],
                        spacing=2,
                    ),
                )
            )

    # ---------------------------------------------------------
    # LIMPIAR ERRORES
    # ---------------------------------------------------------

    def limpiar_errores():

        nombre_error.value = ""
        nombre_error.visible = False

        ruc_error.value = ""
        ruc_error.visible = False

        mensaje.value = ""

    # ---------------------------------------------------------
    # GUARDAR EMPRESA
    # ---------------------------------------------------------

    def guardar_empresa(e):

        limpiar_errores()

        formulario_valido = True

        # Nombre
        valido, error = validar_texto_obligatorio(
            nombre_field.value,
            "Nombre de empresa / cliente",
        )

        if not valido:

            nombre_error.value = error
            nombre_error.visible = True

            formulario_valido = False

        # RUC
        valido, error = validar_ruc(
            ruc_field.value
        )

        if not valido:

            ruc_error.value = error
            ruc_error.visible = True

            formulario_valido = False

        if not formulario_valido:

            mensaje.value = (
                "Corrija los datos indicados."
            )

            mensaje.color = ft.Colors.RED

            page.update()
            return

        # Guardar realmente en Excel.
        guardado, resultado = registrar_empresa(
            nombre_field.value,
            ruc_field.value,
        )

        if not guardado:

            mensaje.value = resultado
            mensaje.color = ft.Colors.RED

            page.update()
            return

        mensaje.value = resultado
        mensaje.color = ft.Colors.GREEN

        nombre_field.value = ""
        ruc_field.value = ""

        refrescar_empresas()

        page.update()

    # ---------------------------------------------------------
    # VOLVER
    # ---------------------------------------------------------

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
                "Registrar empresa",
                size=24,
                weight=ft.FontWeight.BOLD,
            ),
        ],
        spacing=15,
    )

    # ---------------------------------------------------------
    # FORMULARIO
    # ---------------------------------------------------------

    formulario = ft.ResponsiveRow(
        controls=[
            ft.Container(
                col={
                    "xs": 12,
                    "md": 6,
                },
                content=ft.Column(
                    controls=[
                        nombre_field,
                        nombre_error,
                    ],
                ),
            ),
            ft.Container(
                col={
                    "xs": 12,
                    "md": 6,
                },
                content=ft.Column(
                    controls=[
                        ruc_field,
                        ruc_error,
                    ],
                ),
            ),
        ],
    )

    refrescar_empresas()

    # ---------------------------------------------------------
    # MOSTRAR
    # ---------------------------------------------------------

    page.add(
        ft.SafeArea(
            content=ft.Column(
                controls=[
                    encabezado,
                    ft.Divider(),
                    formulario,
                    ft.Button(
                        content="Guardar empresa",
                        on_click=guardar_empresa,
                    ),
                    mensaje,
                    ft.Divider(),
                    ft.Text(
                        "Empresas registradas",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                    ),
                    lista_empresas,
                ],
                spacing=15,
            )
        )
    )