import unicodedata

import flet as ft

from services.producto_service import (
    actualizar_producto,
    listar_productos,
    registrar_producto,
)


def mostrar_productos(
    page: ft.Page,
    volver_menu,
):
    """
    Pantalla de administración del catálogo de productos.

    Permite:
    - registrar productos;
    - editar productos;
    - activar/desactivar;
    - buscar por nombre;
    - buscar por marca;
    - buscar por modelo;
    - buscar por código interno;
    - limitar la cantidad de controles visuales.
    """

    page.clean()

    page.scroll = ft.ScrollMode.AUTO

    # =========================================================
    # CONFIGURACIÓN
    # =========================================================

    LIMITE_RESULTADOS = 15

    # =========================================================
    # PRODUCTO QUE SE ESTÁ EDITANDO
    # =========================================================

    producto_editando_id = {
        "valor": None
    }

    # =========================================================
    # NORMALIZAR TEXTO
    # =========================================================

    def normalizar_texto(texto):

        texto = str(
            texto or ""
        ).strip().casefold()

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
    # CACHÉ
    # =========================================================

    productos_cache = (
        listar_productos()
    )

    def recargar_cache():

        nonlocal productos_cache

        productos_cache = (
            listar_productos()
        )

    # =========================================================
    # CAMPOS
    # =========================================================

    nombre_field = ft.TextField(
        label="Nombre del producto",
        hint_text="Ej: Termostato digital",
    )

    categoria_field = ft.Dropdown(
        label="Categoría",
        value="REPUESTO",
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
                key="OTRO",
                text="Otro",
            ),
        ],
    )

    marca_field = ft.TextField(
        label="Marca",
        hint_text="Ej: Full Gauge",
    )

    modelo_field = ft.TextField(
        label="Modelo",
        hint_text="Ej: MT-512E",
    )

    codigo_field = ft.TextField(
    label="Código asignado",
    value="Se generará al guardar",
    read_only=True,
)

    unidad_field = ft.Dropdown(
        label="Unidad",
        value="UNIDAD",
        options=[
            ft.DropdownOption(
                key="UNIDAD",
                text="Unidad",
            ),
            ft.DropdownOption(
                key="METRO",
                text="Metro",
            ),
            ft.DropdownOption(
                key="KILOGRAMO",
                text="Kilogramo",
            ),
            ft.DropdownOption(
                key="LITRO",
                text="Litro",
            ),
            ft.DropdownOption(
                key="CAJA",
                text="Caja",
            ),
            ft.DropdownOption(
                key="ROLLO",
                text="Rollo",
            ),
            ft.DropdownOption(
                key="OTRO",
                text="Otro",
            ),
        ],
    )

    descripcion_field = ft.TextField(
        label="Descripción / observación",
        hint_text="Información adicional del producto",
        multiline=True,
        min_lines=2,
        max_lines=4,
    )

    activo_field = ft.Checkbox(
        label="Producto activo",
        value=True,
    )

    # =========================================================
    # MENSAJES
    # =========================================================

    nombre_error = ft.Text(
        "",
        color=ft.Colors.RED,
        visible=False,
    )

    categoria_error = ft.Text(
        "",
        color=ft.Colors.RED,
        visible=False,
    )

    mensaje = ft.Text(
        "",
        size=14,
    )

    # =========================================================
    # BUSCADOR
    # =========================================================

    buscar_field = ft.TextField(
        label="Buscar producto",
        hint_text=(
            "Nombre, marca, modelo "
            "o código interno..."
        ),
    )

    informacion_resultados = ft.Text(
        "",
        size=13,
    )

    lista_productos = ft.Column(
        spacing=10,
    )

    # =========================================================
    # LIMPIAR ERRORES
    # =========================================================

    def limpiar_errores():

        nombre_error.value = ""
        nombre_error.visible = False

        categoria_error.value = ""
        categoria_error.visible = False

        mensaje.value = ""

    # =========================================================
    # LIMPIAR FORMULARIO
    # =========================================================

    def limpiar_formulario():

        producto_editando_id[
            "valor"
        ] = None

        nombre_field.value = ""

        categoria_field.value = (
            "REPUESTO"
        )

        marca_field.value = ""

        modelo_field.value = ""

        codigo_field.value = (
        "Se generará al guardar"
)

        unidad_field.value = (
            "UNIDAD"
        )

        descripcion_field.value = ""

        activo_field.value = True

        boton_guardar.content = (
            "Guardar producto"
        )

        boton_cancelar.visible = False

        limpiar_errores()

    # =========================================================
    # FILTRAR PRODUCTOS
    # =========================================================

    def filtrar_productos():

        texto = normalizar_texto(
            buscar_field.value
        )

        productos_ordenados = sorted(
            productos_cache,
            key=lambda producto:
                normalizar_texto(
                    producto["nombre"]
                ),
        )

        if texto == "":

            coincidencias = (
                productos_ordenados
            )

        else:

            coincidencias_inicio = []

            coincidencias_parciales = []

            for producto in (
                productos_ordenados
            ):

                campos = [
                    normalizar_texto(
                        producto["nombre"]
                    ),
                    normalizar_texto(
                        producto["marca"]
                    ),
                    normalizar_texto(
                        producto["modelo"]
                    ),
                    normalizar_texto(
                        producto[
                            "codigo_interno"
                        ]
                    ),
                ]

                if any(
                    campo.startswith(texto)
                    for campo in campos
                    if campo
                ):

                    coincidencias_inicio.append(
                        producto
                    )

                elif any(
                    texto in campo
                    for campo in campos
                    if campo
                ):

                    coincidencias_parciales.append(
                        producto
                    )

            coincidencias = (
                coincidencias_inicio
                + coincidencias_parciales
            )

        total = len(
            coincidencias
        )

        return (
            coincidencias[
                :LIMITE_RESULTADOS
            ],
            total,
        )

    # =========================================================
    # CARGAR PRODUCTO PARA EDITAR
    # =========================================================

    def cargar_para_editar(
        producto,
    ):

        producto_editando_id[
            "valor"
        ] = producto["id"]

        nombre_field.value = (
            producto["nombre"]
        )

        categoria_field.value = (
            producto["categoria"]
        )

        marca_field.value = (
            producto["marca"]
        )

        modelo_field.value = (
            producto["modelo"]
        )

        codigo_field.value = (
            producto["codigo_interno"]
        )

        unidad_field.value = (
            producto["unidad"]
        )

        descripcion_field.value = (
            producto["descripcion"]
        )

        activo_field.value = (
            producto["activo"]
        )

        boton_guardar.content = (
            "Actualizar producto"
        )

        boton_cancelar.visible = True

        mensaje.value = (
            "Editando producto existente."
        )

        mensaje.color = ft.Colors.BLUE

        page.update()

    # =========================================================
    # CREAR TARJETA
    # =========================================================

    def crear_tarjeta(
        producto,
    ):

        if producto["activo"]:

            estado = "ACTIVO"

        else:

            estado = "INACTIVO"

        controles = [
            ft.Text(
                producto["nombre"],
                size=17,
                weight=ft.FontWeight.BOLD,
            ),

            ft.Text(
                f'Categoría: '
                f'{producto["categoria"]}'
            ),

            ft.Text(
                f'Unidad: '
                f'{producto["unidad"]}'
            ),

            ft.Text(
                f'Estado: {estado}'
            ),
        ]

        if producto["marca"]:

            controles.append(
                ft.Text(
                    f'Marca: '
                    f'{producto["marca"]}'
                )
            )

        if producto["modelo"]:

            controles.append(
                ft.Text(
                    f'Modelo: '
                    f'{producto["modelo"]}'
                )
            )

        if producto[
            "codigo_interno"
        ]:

            controles.append(
                ft.Text(
                    f'Código: '
                    f'{producto["codigo_interno"]}'
                )
            )

        if producto[
            "descripcion"
        ]:

            controles.append(
                ft.Text(
                    f'Descripción: '
                    f'{producto["descripcion"]}'
                )
            )

        controles.append(
            ft.Button(
                content="Editar",
                on_click=(
                    lambda e,
                    prod=producto:
                    cargar_para_editar(
                        prod
                    )
                ),
            )
        )

        return ft.Container(
            padding=15,
            border=ft.Border.all(
                width=1,
                color=ft.Colors.OUTLINE,
            ),
            border_radius=10,
            content=ft.Column(
                controls=controles,
                spacing=4,
            ),
        )

    # =========================================================
    # ACTUALIZAR LISTADO
    # =========================================================

    def refrescar_productos():

        lista_productos.controls.clear()

        resultados, total = (
            filtrar_productos()
        )

        if total == 0:

            informacion_resultados.value = (
                "No se encontraron productos."
            )

            lista_productos.controls.append(
                ft.Text(
                    "No existen productos "
                    "para esta búsqueda."
                )
            )

            return

        if total > LIMITE_RESULTADOS:

            informacion_resultados.value = (
                f"Mostrando "
                f"{LIMITE_RESULTADOS} "
                f"de {total} productos."
            )

        else:

            informacion_resultados.value = (
                f"{total} producto(s) "
                f"encontrado(s)."
            )

        for producto in resultados:

            lista_productos.controls.append(
                crear_tarjeta(
                    producto
                )
            )

    # =========================================================
    # BUSCAR
    # =========================================================

    def buscar(e):

        refrescar_productos()

        page.update()

    buscar_field.on_change = buscar

    # =========================================================
    # GUARDAR
    # =========================================================

    def guardar(e):

        limpiar_errores()

        valido = True

        nombre = str(
            nombre_field.value
            or ""
        ).strip()

        categoria = str(
            categoria_field.value
            or ""
        ).strip()

        if nombre == "":

            nombre_error.value = (
                "El nombre del producto "
                "es obligatorio."
            )

            nombre_error.visible = True

            valido = False

        if categoria == "":

            categoria_error.value = (
                "Seleccione una categoría."
            )

            categoria_error.visible = True

            valido = False

        if not valido:

            mensaje.value = (
                "Corrija los datos indicados."
            )

            mensaje.color = ft.Colors.RED

            page.update()

            return

        producto_id = (
            producto_editando_id[
                "valor"
            ]
        )

        # =====================================================
        # NUEVO PRODUCTO
        # =====================================================

        if producto_id is None:

            guardado, resultado = (
                registrar_producto(
    nombre=nombre_field.value,
    categoria=categoria_field.value,
    marca=marca_field.value,
    modelo=modelo_field.value,
    unidad=unidad_field.value,
    descripcion=descripcion_field.value,
    activo=activo_field.value,
)
            )

        # =====================================================
        # EDITAR PRODUCTO
        # =====================================================

        else:

            guardado, resultado = (
                actualizar_producto(
                    producto_id=producto_id,
                    nombre=nombre_field.value,
                    categoria=categoria_field.value,
                    marca=marca_field.value,
                    modelo=modelo_field.value,
                    unidad=unidad_field.value,
                    descripcion=descripcion_field.value,
                    activo=activo_field.value,
)
            )

        # =====================================================
        # ERROR
        # =====================================================

        if not guardado:

            mensaje.value = str(
                resultado
            )

            mensaje.color = ft.Colors.RED

            page.update()

            return

        # =====================================================
        # ÉXITO
        # =====================================================

        if isinstance(
            resultado,
            dict,
        ):

            codigo_asignado = resultado.get(
                "codigo_interno",
                "",
            )

            texto_resultado = resultado["mensaje"]

            if codigo_asignado:

                texto_resultado += (
                    f" Código: "
                    f"{codigo_asignado}"
                )

        else:

            texto_resultado = str(
                resultado
            )

        recargar_cache()

        limpiar_formulario()

        mensaje.value = texto_resultado

        mensaje.color = ft.Colors.GREEN

        refrescar_productos()

        page.update()

    # =========================================================
    # CANCELAR EDICIÓN
    # =========================================================

    def cancelar(e):

        limpiar_formulario()

        refrescar_productos()

        page.update()

    # =========================================================
    # VOLVER
    # =========================================================

    def regresar(e):

        volver_menu()

    # =========================================================
    # BOTONES
    # =========================================================

    boton_guardar = ft.Button(
        content="Guardar producto",
        on_click=guardar,
    )

    boton_cancelar = ft.Button(
        content="Cancelar edición",
        on_click=cancelar,
        visible=False,
    )

    # =========================================================
    # FORMULARIO RESPONSIVE
    # =========================================================

    formulario = ft.ResponsiveRow(
        spacing=15,
        run_spacing=15,
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
                    spacing=5,
                ),
            ),

            ft.Container(
                col={
                    "xs": 12,
                    "md": 6,
                },
                content=ft.Column(
                    controls=[
                        categoria_field,
                        categoria_error,
                    ],
                    spacing=5,
                ),
            ),

            ft.Container(
                col={
                    "xs": 12,
                    "md": 6,
                },
                content=marca_field,
            ),

            ft.Container(
                col={
                    "xs": 12,
                    "md": 6,
                },
                content=modelo_field,
            ),

            ft.Container(
                col={
                    "xs": 12,
                    "md": 6,
                },
                content=codigo_field,
            ),

            ft.Container(
                col={
                    "xs": 12,
                    "md": 6,
                },
                content=unidad_field,
            ),

            ft.Container(
                col={
                    "xs": 12,
                },
                content=descripcion_field,
            ),

            ft.Container(
                col={
                    "xs": 12,
                },
                content=activo_field,
            ),
        ],
    )

    # =========================================================
    # PRIMER LISTADO
    # =========================================================

    refrescar_productos()

    # =========================================================
    # MOSTRAR
    # =========================================================

    page.add(
        ft.SafeArea(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Button(
                                content="← Volver",
                                on_click=regresar,
                            ),

                            ft.Text(
                                "Productos",
                                size=24,
                                weight=(
                                    ft.FontWeight.BOLD
                                ),
                            ),
                        ],
                        spacing=15,
                    ),

                    ft.Divider(),

                    ft.Text(
                        "Datos del producto",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                    ),

                    formulario,

                    ft.Row(
                        controls=[
                            boton_guardar,
                            boton_cancelar,
                        ],
                        spacing=10,
                    ),

                    mensaje,

                    ft.Divider(),

                    ft.Text(
                        "Productos registrados",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                    ),

                    buscar_field,

                    informacion_resultados,

                    lista_productos,
                ],
                spacing=15,
            )
        )
    )