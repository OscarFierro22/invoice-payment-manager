from datetime import datetime

import flet as ft

from services.empresa_service import buscar_empresas

from utils.validators import (
    validar_fecha,
    validar_ruc,
    validar_texto_obligatorio,
    validar_total,
)


def mostrar_registro_factura(page: ft.Page, volver_menu):
    """
    Muestra el formulario para registrar una factura.

    Funciones actuales:
    - Buscar empresas por nombre.
    - Buscar empresas por RUC.
    - Autocompletar nombre y RUC.
    - Escribir fecha manualmente.
    - Seleccionar fecha desde calendario.
    - Validar los datos ingresados.

    Todavía no guarda la factura en Excel.
    """

    page.clean()

    # =========================================================
    # MENSAJES DE ERROR
    # =========================================================

    empresa_error = ft.Text(
        "",
        color=ft.Colors.RED,
        size=13,
        visible=False,
    )

    ruc_error = ft.Text(
        "",
        color=ft.Colors.RED,
        size=13,
        visible=False,
    )

    numero_factura_error = ft.Text(
        "",
        color=ft.Colors.RED,
        size=13,
        visible=False,
    )

    fecha_emision_error = ft.Text(
        "",
        color=ft.Colors.RED,
        size=13,
        visible=False,
    )

    total_error = ft.Text(
        "",
        color=ft.Colors.RED,
        size=13,
        visible=False,
    )

    mensaje = ft.Text(
        "",
        size=14,
    )

    # =========================================================
    # LISTAS DE SUGERENCIAS
    # =========================================================

    sugerencias_empresa = ft.Column(
        spacing=5,
        visible=False,
    )

    sugerencias_ruc = ft.Column(
        spacing=5,
        visible=False,
    )

    # =========================================================
    # CAMPOS DEL FORMULARIO
    # =========================================================

    empresa_field = ft.TextField(
        label="Empresa / Cliente",
        hint_text="Empiece a escribir el nombre...",
    )

    ruc_field = ft.TextField(
        label="RUC",
        hint_text="Empiece a escribir el RUC...",
        max_length=13,
    )

    numero_factura_field = ft.TextField(
        label="Número de factura",
        hint_text="001-001-000000001",
    )

    fecha_emision_field = ft.TextField(
        label="Fecha de emisión",
        hint_text="dd/mm/aaaa",
    )

    total_field = ft.TextField(
        label="Valor total",
        hint_text="0.00",
    )

    # =========================================================
    # AUTOCOMPLETADO DE EMPRESAS
    # =========================================================

    def seleccionar_empresa(empresa):
        """
        Completa automáticamente los campos de nombre y RUC
        cuando el usuario selecciona una empresa.
        """

        empresa_field.value = empresa["nombre"]
        ruc_field.value = empresa["ruc"]

        # Ocultar sugerencias.
        sugerencias_empresa.controls.clear()
        sugerencias_ruc.controls.clear()

        sugerencias_empresa.visible = False
        sugerencias_ruc.visible = False

        # Quitar errores anteriores.
        empresa_error.value = ""
        empresa_error.visible = False

        ruc_error.value = ""
        ruc_error.visible = False

        page.update()

    def crear_opcion_empresa(empresa):
        """
        Crea un botón para cada resultado encontrado.
        """

        texto = (
            f'{empresa["nombre"]} '
            f'— RUC: {empresa["ruc"]}'
        )

        return ft.Button(
            content=texto,
            on_click=lambda e, emp=empresa: seleccionar_empresa(emp),
        )

    def buscar_por_nombre(e):
        """
        Busca coincidencias mientras el usuario escribe
        el nombre de la empresa.
        """

        texto = empresa_field.value or ""

        sugerencias_empresa.controls.clear()

        if texto.strip() == "":
            sugerencias_empresa.visible = False
            page.update()
            return

        resultados = buscar_empresas(
            texto,
            campo="nombre",
        )

        if not resultados:
            sugerencias_empresa.visible = False
            page.update()
            return

        for empresa in resultados:
            sugerencias_empresa.controls.append(
                crear_opcion_empresa(empresa)
            )

        sugerencias_empresa.visible = True

        # Ocultamos las sugerencias del otro campo.
        sugerencias_ruc.visible = False

        page.update()

    def buscar_por_ruc(e):
        """
        Busca coincidencias mientras el usuario escribe
        el RUC.
        """

        texto = ruc_field.value or ""

        sugerencias_ruc.controls.clear()

        if texto.strip() == "":
            sugerencias_ruc.visible = False
            page.update()
            return

        resultados = buscar_empresas(
            texto,
            campo="ruc",
        )

        if not resultados:
            sugerencias_ruc.visible = False
            page.update()
            return

        for empresa in resultados:
            sugerencias_ruc.controls.append(
                crear_opcion_empresa(empresa)
            )

        sugerencias_ruc.visible = True

        # Ocultamos las sugerencias del otro campo.
        sugerencias_empresa.visible = False

        page.update()

    # Conectamos los eventos después de crear las funciones.
    empresa_field.on_change = buscar_por_nombre
    ruc_field.on_change = buscar_por_ruc

    # =========================================================
    # CALENDARIO
    # =========================================================

    def fecha_seleccionada(e):
        """
        Copia al campo de fecha el día escogido
        en el calendario.
        """

        if selector_fecha.value is None:
            return

        fecha_emision_field.value = (
            selector_fecha.value.strftime("%d/%m/%Y")
        )

        fecha_emision_error.value = ""
        fecha_emision_error.visible = False

        page.update()

    selector_fecha = ft.DatePicker(
        first_date=datetime(2020, 1, 1),
        last_date=datetime(2035, 12, 31),
        current_date=datetime.now(),
        on_change=fecha_seleccionada,
    )

    def abrir_calendario(e):
        page.show_dialog(selector_fecha)

    # =========================================================
    # FUNCIONES DE ERROR
    # =========================================================

    def mostrar_error(control_error, texto):
        """
        Muestra un mensaje debajo del campo incorrecto.
        """

        control_error.value = texto
        control_error.visible = True

    def limpiar_errores():
        """
        Limpia todos los mensajes de error anteriores.
        """

        empresa_error.value = ""
        empresa_error.visible = False

        ruc_error.value = ""
        ruc_error.visible = False

        numero_factura_error.value = ""
        numero_factura_error.visible = False

        fecha_emision_error.value = ""
        fecha_emision_error.visible = False

        total_error.value = ""
        total_error.visible = False

        mensaje.value = ""

    # =========================================================
    # VALIDACIÓN DEL FORMULARIO
    # =========================================================

    def guardar_factura(e):
        limpiar_errores()

        formulario_valido = True

        # -----------------------------------------------------
        # EMPRESA
        # -----------------------------------------------------

        valido, error = validar_texto_obligatorio(
            empresa_field.value,
            "Empresa / Cliente",
        )

        if not valido:
            mostrar_error(
                empresa_error,
                error,
            )

            formulario_valido = False

        # -----------------------------------------------------
        # RUC
        # -----------------------------------------------------

        valido, error = validar_ruc(
            ruc_field.value,
        )

        if not valido:
            mostrar_error(
                ruc_error,
                error,
            )

            formulario_valido = False

        # -----------------------------------------------------
        # NÚMERO DE FACTURA
        # -----------------------------------------------------

        valido, error = validar_texto_obligatorio(
            numero_factura_field.value,
            "Número de factura",
        )

        if not valido:
            mostrar_error(
                numero_factura_error,
                error,
            )

            formulario_valido = False

        # -----------------------------------------------------
        # FECHA DE EMISIÓN
        # -----------------------------------------------------

        valido, resultado_fecha = validar_fecha(
            fecha_emision_field.value,
        )

        if not valido:
            mostrar_error(
                fecha_emision_error,
                resultado_fecha,
            )

            formulario_valido = False

        # -----------------------------------------------------
        # TOTAL
        # -----------------------------------------------------

        valido, resultado_total = validar_total(
            total_field.value,
        )

        if not valido:
            mostrar_error(
                total_error,
                resultado_total,
            )

            formulario_valido = False

        # -----------------------------------------------------
        # RESULTADO
        # -----------------------------------------------------

        if not formulario_valido:
            mensaje.value = "Corrija los datos indicados."
            mensaje.color = ft.Colors.RED

            page.update()
            return

        mensaje.value = (
            "Datos correctos. "
            "La factura está lista para ser guardada."
        )

        mensaje.color = ft.Colors.GREEN

        page.update()

    # =========================================================
    # NAVEGACIÓN
    # =========================================================

    def regresar(e):
        volver_menu()

    # =========================================================
    # ENCABEZADO
    # =========================================================

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

    # =========================================================
    # GRUPO EMPRESA
    # =========================================================

    empresa_control = ft.Column(
        controls=[
            empresa_field,
            sugerencias_empresa,
            empresa_error,
        ],
        spacing=5,
    )

    # =========================================================
    # GRUPO RUC
    # =========================================================

    ruc_control = ft.Column(
        controls=[
            ruc_field,
            sugerencias_ruc,
            ruc_error,
        ],
        spacing=5,
    )

    # =========================================================
    # GRUPO NÚMERO DE FACTURA
    # =========================================================

    numero_factura_control = ft.Column(
        controls=[
            numero_factura_field,
            numero_factura_error,
        ],
        spacing=5,
    )

    # =========================================================
    # GRUPO FECHA
    # =========================================================

    fecha_emision_control = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Container(
                        content=fecha_emision_field,
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CALENDAR_MONTH,
                        tooltip="Seleccionar fecha",
                        on_click=abrir_calendario,
                    ),
                ],
            ),
            fecha_emision_error,
        ],
        spacing=5,
    )

    # =========================================================
    # GRUPO TOTAL
    # =========================================================

    total_control = ft.Column(
        controls=[
            total_field,
            total_error,
        ],
        spacing=5,
    )

    # =========================================================
    # FORMULARIO RESPONSIVE
    # =========================================================

    formulario = ft.ResponsiveRow(
        spacing=15,
        run_spacing=15,
        controls=[
            ft.Container(
                content=empresa_control,
                col={
                    "xs": 12,
                    "md": 6,
                },
            ),
            ft.Container(
                content=ruc_control,
                col={
                    "xs": 12,
                    "md": 6,
                },
            ),
            ft.Container(
                content=numero_factura_control,
                col={
                    "xs": 12,
                    "md": 6,
                },
            ),
            ft.Container(
                content=fecha_emision_control,
                col={
                    "xs": 12,
                    "md": 6,
                },
            ),
            ft.Container(
                content=total_control,
                col={
                    "xs": 12,
                    "md": 6,
                },
            ),
        ],
    )

    # =========================================================
    # BOTONES
    # =========================================================

    acciones = ft.Row(
        controls=[
            ft.Button(
                content="Guardar factura",
                on_click=guardar_factura,
            ),
        ],
    )
    # =========================================================
    # MOSTRAR PANTALLA
    # =========================================================

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