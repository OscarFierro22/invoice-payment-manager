from datetime import datetime
import unicodedata

import flet as ft

from services.empresa_service import listar_empresas

from services.factura_service import (
    calcular_totales,
    registrar_factura,
)

from utils.validators import (
    validar_credito_dias,
    validar_fecha,
    validar_texto_obligatorio,
)


def mostrar_registro_factura(
    page: ft.Page,
    volver_menu,
):
    """
    Pantalla para registrar una factura completa.

    Permite:

    - Seleccionar un cliente.
    - Buscarlo por nombre o RUC.
    - Obtener su crédito predeterminado.
    - Registrar varios detalles.
    - Calcular subtotal, IVA y total.
    - Guardar factura y detalles en Excel.
    """

    page.clean()

    page.scroll = ft.ScrollMode.AUTO

    # =========================================================
    # CONFIGURACIÓN
    # =========================================================

    LIMITE_SUGERENCIAS = 8

    # =========================================================
    # EMPRESA SELECCIONADA
    # =========================================================

    empresa_seleccionada_id = {
        "valor": None
    }

    # =========================================================
    # DETALLES TEMPORALES DE LA FACTURA
    # =========================================================

    detalles_factura = []

    # =========================================================
    # NORMALIZACIÓN PARA BÚSQUEDA
    # =========================================================

    def normalizar_texto(texto):
        """
        Convierte texto a una forma apropiada para búsqueda.

        Ejemplos:

            Río Amazonas
                ↓
            rio amazonas

            SHERATON
                ↓
            sheraton
        """

        texto = str(
            texto or ""
        ).strip().lower()

        texto = unicodedata.normalize(
            "NFD",
            texto,
        )

        texto = "".join(
            caracter
            for caracter in texto
            if unicodedata.category(
                caracter
            ) != "Mn"
        )

        return texto

    # =========================================================
    # CARGAR CLIENTES UNA SOLA VEZ
    # =========================================================

    empresas_excel = listar_empresas()

    empresas_cache = []

    for empresa in empresas_excel:

        # No mostrar empresas inactivas.
        if not empresa["activo"]:
            continue

        # Solamente clientes o empresas de tipo AMBOS
        # pueden ser receptores de una factura.
        if empresa["tipo"] not in {
            "CLIENTE",
            "AMBOS",
        }:
            continue

        empresas_cache.append(
            empresa
        )

    # =========================================================
    # CAMPOS PRINCIPALES DE FACTURA
    # =========================================================

    cliente_field = ft.TextField(
        label="Cliente",
        hint_text="Buscar por nombre o RUC...",
    )

    ruc_field = ft.TextField(
        label="RUC",
        read_only=True,
    )

    numero_factura_field = ft.TextField(
        label="Número de factura",
        hint_text="Ej: 001-001-000000150",
    )

    fecha_field = ft.TextField(
        label="Fecha de emisión",
        hint_text="dd/mm/aaaa",
        value=datetime.now().strftime(
            "%d/%m/%Y"
        ),
    )

    credito_field = ft.TextField(
        label="Crédito",
        value="0",
        suffix="días",
    )

    iva_porcentaje_field = ft.TextField(
        label="IVA",
        value="15",
        suffix="%",
    )

    # =========================================================
    # SUGERENCIAS DE EMPRESA
    # =========================================================

    sugerencias_empresas = ft.Column(
        spacing=5,
        visible=False,
    )

    # =========================================================
    # ERRORES DE CABECERA
    # =========================================================

    cliente_error = ft.Text(
        "",
        color=ft.Colors.RED,
        visible=False,
    )

    numero_factura_error = ft.Text(
        "",
        color=ft.Colors.RED,
        visible=False,
    )

    fecha_error = ft.Text(
        "",
        color=ft.Colors.RED,
        visible=False,
    )

    credito_error = ft.Text(
        "",
        color=ft.Colors.RED,
        visible=False,
    )

    iva_error = ft.Text(
        "",
        color=ft.Colors.RED,
        visible=False,
    )

    # =========================================================
    # CAMPOS PARA AGREGAR DETALLES
    # =========================================================

    tipo_item_field = ft.Dropdown(
        label="Tipo",
        value="MANTENIMIENTO",
        options=[
            ft.DropdownOption(
                key="EQUIPO",
                text="Equipo",
            ),
            ft.DropdownOption(
                key="REPUESTO",
                text="Repuesto",
            ),
            ft.DropdownOption(
                key="MATERIAL",
                text="Material",
            ),
            ft.DropdownOption(
                key="SERVICIO",
                text="Servicio",
            ),
            ft.DropdownOption(
                key="MANTENIMIENTO",
                text="Mantenimiento",
            ),
            ft.DropdownOption(
                key="MANO_DE_OBRA",
                text="Mano de obra",
            ),
            ft.DropdownOption(
                key="OTRO",
                text="Otro",
            ),
        ],
    )

    descripcion_field = ft.TextField(
        label="Descripción",
        hint_text=(
            "Ej: Mantenimiento preventivo "
            "de cámara frigorífica"
        ),
    )

    cantidad_field = ft.TextField(
        label="Cantidad",
        value="1",
    )

    precio_unitario_field = ft.TextField(
        label="Precio unitario",
        hint_text="Ej: 150.00",
        prefix="$",
    )

    detalle_error = ft.Text(
        "",
        color=ft.Colors.RED,
        visible=False,
    )

    # =========================================================
    # LISTA VISUAL DE DETALLES
    # =========================================================

    lista_detalles = ft.Column(
        spacing=10,
    )

    # =========================================================
    # TOTALES
    # =========================================================

    subtotal_text = ft.Text(
        "Subtotal: $0.00",
        size=16,
    )

    iva_text = ft.Text(
        "IVA: $0.00",
        size=16,
    )

    total_text = ft.Text(
        "TOTAL: $0.00",
        size=20,
        weight=ft.FontWeight.BOLD,
    )

    mensaje_general = ft.Text(
        "",
        size=14,
    )

    # =========================================================
    # LIMPIAR ERRORES
    # =========================================================

    def limpiar_errores_factura():

        cliente_error.value = ""
        cliente_error.visible = False

        numero_factura_error.value = ""
        numero_factura_error.visible = False

        fecha_error.value = ""
        fecha_error.visible = False

        credito_error.value = ""
        credito_error.visible = False

        iva_error.value = ""
        iva_error.visible = False

    # =========================================================
    # SELECCIONAR EMPRESA
    # =========================================================

    def seleccionar_empresa(
        empresa,
    ):
        """
        Guarda internamente el ID de la empresa
        y llena sus datos visibles.
        """

        empresa_seleccionada_id[
            "valor"
        ] = empresa["id"]

        cliente_field.value = (
            empresa["nombre"]
        )

        ruc_field.value = (
            empresa["ruc"]
        )

        credito_field.value = str(
            empresa["credito_dias"]
        )

        sugerencias_empresas.controls.clear()

        sugerencias_empresas.visible = False

        cliente_error.visible = False

        page.update()

    # =========================================================
    # BUSCAR EMPRESAS
    # =========================================================

    def buscar_empresa(e):
        """
        Filtra empresas en memoria.

        No abre Excel mientras el usuario escribe.
        """

        # Si el usuario modifica el texto después de haber
        # seleccionado una empresa, la selección anterior
        # deja de ser válida.
        empresa_seleccionada_id[
            "valor"
        ] = None

        ruc_field.value = ""

        texto = normalizar_texto(
            cliente_field.value
        )

        sugerencias_empresas.controls.clear()

        if texto == "":

            sugerencias_empresas.visible = False

            page.update()

            return

        coincidencias_inicio = []
        coincidencias_parciales = []

        for empresa in empresas_cache:

            nombre = normalizar_texto(
                empresa["nombre"]
            )

            ruc = str(
                empresa["ruc"]
            ).strip()

            # -----------------------------------------------
            # PRIORIDAD 1:
            # empieza con el texto buscado.
            # -----------------------------------------------

            if (
                nombre.startswith(texto)
                or ruc.startswith(texto)
            ):

                coincidencias_inicio.append(
                    empresa
                )

            # -----------------------------------------------
            # PRIORIDAD 2:
            # contiene el texto buscado.
            # -----------------------------------------------

            elif (
                texto in nombre
                or texto in ruc
            ):

                coincidencias_parciales.append(
                    empresa
                )

        coincidencias = (
            coincidencias_inicio
            + coincidencias_parciales
        )

        coincidencias = coincidencias[
            :LIMITE_SUGERENCIAS
        ]

        if not coincidencias:

            sugerencias_empresas.controls.append(
                ft.Text(
                    "No se encontraron clientes."
                )
            )

        else:

            for empresa in coincidencias:

                sugerencias_empresas.controls.append(
                    ft.Button(
                        content=(
                            f'{empresa["nombre"]} '
                            f'— {empresa["ruc"]}'
                        ),
                        on_click=(
                            lambda e, emp=empresa:
                            seleccionar_empresa(
                                emp
                            )
                        ),
                    )
                )

        sugerencias_empresas.visible = True

        page.update()

    cliente_field.on_change = buscar_empresa

    # =========================================================
    # CALENDARIO
    # =========================================================

    def seleccionar_fecha(e):

        if selector_fecha.value is None:
            return

        fecha_field.value = (
            selector_fecha.value.strftime(
                "%d/%m/%Y"
            )
        )

        page.update()

    selector_fecha = ft.DatePicker(
        on_change=seleccionar_fecha,
    )

    def abrir_calendario(e):

        page.show_dialog(
            selector_fecha
        )

    boton_calendario = ft.Button(
        content="Calendario",
        on_click=abrir_calendario,
    )

    # =========================================================
    # ACTUALIZAR TOTALES
    # =========================================================

    def actualizar_totales():
        """
        Calcula los totales utilizando solamente
        los detalles que existen en memoria.

        No toca Excel.
        """

        iva_error.value = ""
        iva_error.visible = False

        if not detalles_factura:

            subtotal_text.value = (
                "Subtotal: $0.00"
            )

            iva_text.value = (
                "IVA: $0.00"
            )

            total_text.value = (
                "TOTAL: $0.00"
            )

            return

        try:

            resultado = calcular_totales(
                detalles=detalles_factura,
                iva_porcentaje=(
                    iva_porcentaje_field.value
                ),
            )

        except ValueError as error:

            subtotal_text.value = (
                "Subtotal: —"
            )

            iva_text.value = (
                "IVA: —"
            )

            total_text.value = (
                "TOTAL: —"
            )

            iva_error.value = str(
                error
            )

            iva_error.visible = True

            return

        subtotal_text.value = (
            f'Subtotal: '
            f'${resultado["subtotal"]:.2f}'
        )

        iva_text.value = (
            f'IVA '
            f'({resultado["iva_porcentaje"]}%): '
            f'${resultado["iva"]:.2f}'
        )

        total_text.value = (
            f'TOTAL: '
            f'${resultado["total"]:.2f}'
        )

    # =========================================================
    # CAMBIAR IVA
    # =========================================================

    def cambiar_iva(e):

        actualizar_totales()

        page.update()

    iva_porcentaje_field.on_change = (
        cambiar_iva
    )

    # =========================================================
    # ELIMINAR DETALLE
    # =========================================================

    def eliminar_detalle(
        indice,
    ):

        if (
            indice < 0
            or indice >= len(
                detalles_factura
            )
        ):
            return

        detalles_factura.pop(
            indice
        )

        refrescar_detalles()

        actualizar_totales()

        page.update()

    # =========================================================
    # CREAR TARJETA DEL DETALLE
    # =========================================================

    def crear_tarjeta_detalle(
        detalle,
        indice,
    ):

        tipo_mostrado = (
            detalle["tipo_item"]
            .replace(
                "_",
                " ",
            )
            .title()
        )

        cantidad = detalle[
            "cantidad"
        ]

        precio = detalle[
            "precio_unitario"
        ]

        subtotal = detalle[
            "subtotal"
        ]

        return ft.Container(
            padding=12,
            border=ft.Border.all(
                width=1,
                color=ft.Colors.OUTLINE,
            ),
            border_radius=10,
            content=ft.Column(
                controls=[
                    ft.Text(
                        detalle[
                            "descripcion"
                        ],
                        weight=(
                            ft.FontWeight.BOLD
                        ),
                    ),
                    ft.Text(
                        f"Tipo: {tipo_mostrado}"
                    ),
                    ft.Text(
                        f"Cantidad: {cantidad}"
                    ),
                    ft.Text(
                        f"Precio unitario: "
                        f"${precio:.2f}"
                    ),
                    ft.Text(
                        f"Subtotal: "
                        f"${subtotal:.2f}"
                    ),
                    ft.Button(
                        content="Eliminar",
                        on_click=(
                            lambda e,
                            posicion=indice:
                            eliminar_detalle(
                                posicion
                            )
                        ),
                    ),
                ],
                spacing=4,
            ),
        )

    # =========================================================
    # REFRESCAR DETALLES
    # =========================================================

    def refrescar_detalles():

        lista_detalles.controls.clear()

        if not detalles_factura:

            lista_detalles.controls.append(
                ft.Text(
                    "Todavía no se han agregado "
                    "ítems a la factura."
                )
            )

            return

        for indice, detalle in enumerate(
            detalles_factura
        ):

            lista_detalles.controls.append(
                crear_tarjeta_detalle(
                    detalle,
                    indice,
                )
            )

    # =========================================================
    # AGREGAR DETALLE
    # =========================================================

    def agregar_detalle(e):

        detalle_error.value = ""
        detalle_error.visible = False

        detalle_nuevo = {
            "tipo_item":
                tipo_item_field.value,

            "descripcion":
                descripcion_field.value,

            "cantidad":
                cantidad_field.value,

            "precio_unitario":
                precio_unitario_field.value,

            "id_compra":
                None,
        }

        # -----------------------------------------------------
        # USAMOS EL MISMO MOTOR DE FACTURAS PARA VALIDAR
        # -----------------------------------------------------

        try:

            resultado = calcular_totales(
                detalles=[
                    detalle_nuevo
                ],
                iva_porcentaje=0,
            )

        except ValueError as error:

            detalle_error.value = str(
                error
            )

            detalle_error.visible = True

            page.update()

            return

        # -----------------------------------------------------
        # OBTENER VERSIÓN NORMALIZADA
        # -----------------------------------------------------

        detalle_normalizado = (
            resultado[
                "detalles"
            ][0]
        )

        # -----------------------------------------------------
        # AGREGAR SOLO A MEMORIA
        # -----------------------------------------------------

        detalles_factura.append(
            detalle_normalizado
        )

        # -----------------------------------------------------
        # LIMPIAR CAMPOS DEL DETALLE
        # -----------------------------------------------------

        descripcion_field.value = ""

        cantidad_field.value = "1"

        precio_unitario_field.value = ""

        # Dejamos el tipo seleccionado porque muchas veces
        # se agregan varios conceptos del mismo tipo.

        refrescar_detalles()

        actualizar_totales()

        page.update()

    boton_agregar_detalle = ft.Button(
        content="+ Agregar detalle",
        on_click=agregar_detalle,
    )

    # =========================================================
    # LIMPIAR FACTURA COMPLETA
    # =========================================================

    def limpiar_factura():

        empresa_seleccionada_id[
            "valor"
        ] = None

        cliente_field.value = ""

        ruc_field.value = ""

        numero_factura_field.value = ""

        fecha_field.value = (
            datetime.now().strftime(
                "%d/%m/%Y"
            )
        )

        credito_field.value = "0"

        iva_porcentaje_field.value = "15"

        detalles_factura.clear()

        sugerencias_empresas.controls.clear()

        sugerencias_empresas.visible = False

        descripcion_field.value = ""

        cantidad_field.value = "1"

        precio_unitario_field.value = ""

        tipo_item_field.value = (
            "MANTENIMIENTO"
        )

        limpiar_errores_factura()

        detalle_error.value = ""
        detalle_error.visible = False

        refrescar_detalles()

        actualizar_totales()

    # =========================================================
    # GUARDAR FACTURA
    # =========================================================

    def guardar_factura(e):

        limpiar_errores_factura()

        mensaje_general.value = ""

        formulario_valido = True

        # -----------------------------------------------------
        # CLIENTE
        # -----------------------------------------------------

        if (
            empresa_seleccionada_id[
                "valor"
            ]
            is None
        ):

            cliente_error.value = (
                "Seleccione un cliente "
                "de las sugerencias."
            )

            cliente_error.visible = True

            formulario_valido = False

        # -----------------------------------------------------
        # NÚMERO DE FACTURA
        # -----------------------------------------------------

        valido, error = (
            validar_texto_obligatorio(
                numero_factura_field.value,
                "Número de factura",
            )
        )

        if not valido:

            numero_factura_error.value = (
                error
            )

            numero_factura_error.visible = (
                True
            )

            formulario_valido = False

        # -----------------------------------------------------
        # FECHA
        # -----------------------------------------------------

        valido, resultado_fecha = (
            validar_fecha(
                fecha_field.value
            )
        )

        if not valido:

            fecha_error.value = (
                resultado_fecha
            )

            fecha_error.visible = True

            formulario_valido = False

        # -----------------------------------------------------
        # CRÉDITO
        # -----------------------------------------------------

        valido, resultado_credito = (
            validar_credito_dias(
                credito_field.value
            )
        )

        if not valido:

            credito_error.value = (
                resultado_credito
            )

            credito_error.visible = True

            formulario_valido = False

        # -----------------------------------------------------
        # DETALLES
        # -----------------------------------------------------

        if not detalles_factura:

            detalle_error.value = (
                "La factura debe contener "
                "al menos un detalle."
            )

            detalle_error.visible = True

            formulario_valido = False

        # -----------------------------------------------------
        # IVA
        # -----------------------------------------------------

        if detalles_factura:

            try:

                calcular_totales(
                    detalles=detalles_factura,
                    iva_porcentaje=(
                        iva_porcentaje_field.value
                    ),
                )

            except ValueError as error:

                iva_error.value = str(
                    error
                )

                iva_error.visible = True

                formulario_valido = False

        # -----------------------------------------------------
        # DETENER SI EXISTEN ERRORES
        # -----------------------------------------------------

        if not formulario_valido:

            mensaje_general.value = (
                "Corrija los datos indicados."
            )

            mensaje_general.color = (
                ft.Colors.RED
            )

            page.update()

            return

        # =====================================================
        # GUARDAR
        # =====================================================

        guardado, resultado = (
            registrar_factura(
                id_empresa=(
                    empresa_seleccionada_id[
                        "valor"
                    ]
                ),
                empresa=cliente_field.value,
                ruc=ruc_field.value,
                numero_factura=(
                    numero_factura_field.value
                ),
                fecha_emision=(
                    fecha_field.value
                ),
                credito_dias=(
                    resultado_credito
                ),
                iva_porcentaje=(
                    iva_porcentaje_field.value
                ),
                detalles=detalles_factura,
            )
        )

        # -----------------------------------------------------
        # ERROR
        # -----------------------------------------------------

        if not guardado:

            mensaje_general.value = str(
                resultado
            )

            mensaje_general.color = (
                ft.Colors.RED
            )

            page.update()

            return

        # -----------------------------------------------------
        # ÉXITO
        # -----------------------------------------------------

        id_factura = resultado[
            "id_factura"
        ]

        total = resultado[
            "total"
        ]

        mensaje_exito = (
            f"Factura registrada correctamente. "
            f"ID interno: {id_factura}. "
            f"Total: ${total:.2f}"
        )

        limpiar_factura()

        mensaje_general.value = (
            mensaje_exito
        )

        mensaje_general.color = (
            ft.Colors.GREEN
        )

        page.update()

    # =========================================================
    # VOLVER
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
    # DATOS DE FACTURA
    # =========================================================

    datos_factura = ft.ResponsiveRow(
        spacing=15,
        run_spacing=15,
        controls=[
            # -------------------------------------------------
            # CLIENTE
            # -------------------------------------------------

            ft.Container(
                col={
                    "xs": 12,
                    "md": 6,
                },
                content=ft.Column(
                    controls=[
                        cliente_field,
                        cliente_error,
                        sugerencias_empresas,
                    ],
                    spacing=5,
                ),
            ),

            # -------------------------------------------------
            # RUC
            # -------------------------------------------------

            ft.Container(
                col={
                    "xs": 12,
                    "md": 6,
                },
                content=ruc_field,
            ),

            # -------------------------------------------------
            # NÚMERO
            # -------------------------------------------------

            ft.Container(
                col={
                    "xs": 12,
                    "md": 6,
                },
                content=ft.Column(
                    controls=[
                        numero_factura_field,
                        numero_factura_error,
                    ],
                    spacing=5,
                ),
            ),

            # -------------------------------------------------
            # FECHA
            # -------------------------------------------------

            ft.Container(
                col={
                    "xs": 12,
                    "md": 6,
                },
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                fecha_field,
                                boton_calendario,
                            ]
                        ),
                        fecha_error,
                    ],
                    spacing=5,
                ),
            ),

            # -------------------------------------------------
            # CRÉDITO
            # -------------------------------------------------

            ft.Container(
                col={
                    "xs": 12,
                    "md": 6,
                },
                content=ft.Column(
                    controls=[
                        credito_field,
                        credito_error,
                    ],
                    spacing=5,
                ),
            ),

            # -------------------------------------------------
            # IVA
            # -------------------------------------------------

            ft.Container(
                col={
                    "xs": 12,
                    "md": 6,
                },
                content=ft.Column(
                    controls=[
                        iva_porcentaje_field,
                        iva_error,
                    ],
                    spacing=5,
                ),
            ),
        ],
    )

    # =========================================================
    # FORMULARIO DE DETALLE
    # =========================================================

    formulario_detalle = ft.ResponsiveRow(
        spacing=15,
        run_spacing=15,
        controls=[
            ft.Container(
                col={
                    "xs": 12,
                    "md": 6,
                },
                content=tipo_item_field,
            ),

            ft.Container(
                col={
                    "xs": 12,
                    "md": 6,
                },
                content=descripcion_field,
            ),

            ft.Container(
                col={
                    "xs": 12,
                    "md": 6,
                },
                content=cantidad_field,
            ),

            ft.Container(
                col={
                    "xs": 12,
                    "md": 6,
                },
                content=precio_unitario_field,
            ),
        ],
    )

    # =========================================================
    # PRIMER ESTADO
    # =========================================================

    refrescar_detalles()

    actualizar_totales()

    # =========================================================
    # MOSTRAR PANTALLA
    # =========================================================

    page.add(
        ft.SafeArea(
            content=ft.Column(
                controls=[
                    encabezado,

                    ft.Divider(),

                    # =========================================
                    # CABECERA DE FACTURA
                    # =========================================

                    ft.Text(
                        "Datos de la factura",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                    ),

                    datos_factura,

                    ft.Divider(),

                    # =========================================
                    # NUEVO DETALLE
                    # =========================================

                    ft.Text(
                        "Agregar detalle",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                    ),

                    ft.Text(
                        "Agregue equipos, repuestos, "
                        "materiales, servicios, "
                        "mantenimientos o mano de obra."
                    ),

                    formulario_detalle,

                    detalle_error,

                    boton_agregar_detalle,

                    ft.Divider(),

                    # =========================================
                    # DETALLES ACTUALES
                    # =========================================

                    ft.Text(
                        "Detalle de factura",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                    ),

                    lista_detalles,

                    ft.Divider(),

                    # =========================================
                    # TOTALES
                    # =========================================

                    ft.Text(
                        "Resumen",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                    ),

                    subtotal_text,
                    iva_text,
                    total_text,

                    ft.Divider(),

                    ft.Button(
                        content="Guardar factura",
                        on_click=guardar_factura,
                    ),

                    mensaje_general,
                ],
                spacing=15,
            )
        )
    )