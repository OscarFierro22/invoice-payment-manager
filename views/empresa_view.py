import unicodedata

import flet as ft

from services.empresa_service import (
    actualizar_empresa,
    listar_empresas,
    registrar_empresa,
)

from utils.validators import (
    validar_credito_dias,
    validar_email,
    validar_ruc,
    validar_texto_obligatorio,
    validar_tipo_empresa,
)


def mostrar_registro_empresa(
    page: ft.Page,
    volver_menu,
):
    """
    Gestión de empresas.

    Permite:
    - Registrar empresas.
    - Editar empresas existentes.
    - Buscar por nombre o RUC.
    - Trabajar con clientes, proveedores o ambos.
    - Activar/desactivar empresas.
    - Mantener las empresas en caché para evitar
      leer Excel en cada búsqueda.
    """

    page.clean()

    # Toda la página podrá desplazarse verticalmente.
    page.scroll = ft.ScrollMode.AUTO

    # =========================================================
    # CONFIGURACIÓN
    # =========================================================

    LIMITE_RESULTADOS = 15

    # =========================================================
    # EMPRESA QUE SE ESTÁ EDITANDO
    # =========================================================

    empresa_editando_id = {
        "valor": None
    }

    # =========================================================
    # NORMALIZAR TEXTO PARA BÚSQUEDA
    # =========================================================

    def normalizar_texto(texto):
        """
        Prepara texto para realizar búsquedas.

        Ejemplos:

        "Río Amazonas" -> "rio amazonas"
        "RÍO AMAZONAS" -> "rio amazonas"
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
    # CACHÉ DE EMPRESAS
    # =========================================================

    empresas_cache = listar_empresas()

    def recargar_cache():
        """
        Vuelve a leer las empresas desde Excel.

        Solo la utilizamos después de crear o modificar
        una empresa.
        """

        nonlocal empresas_cache

        empresas_cache = listar_empresas()

    # =========================================================
    # CAMPOS DEL FORMULARIO
    # =========================================================

    nombre_field = ft.TextField(
        label="Nombre de empresa",
        hint_text="Ej: Hotel Río Amazonas",
    )

    ruc_field = ft.TextField(
        label="RUC",
        hint_text="13 dígitos",
        max_length=13,
    )

    direccion_field = ft.TextField(
        label="Dirección",
        hint_text="Dirección de la empresa",
    )

    email_field = ft.TextField(
        label="Correo electrónico",
        hint_text="Ej: contabilidad@empresa.com",
    )

    tipo_field = ft.Dropdown(
        label="Tipo de empresa",
        value="CLIENTE",
        options=[
            ft.DropdownOption(
                key="CLIENTE",
                text="Cliente",
            ),
            ft.DropdownOption(
                key="PROVEEDOR",
                text="Proveedor",
            ),
            ft.DropdownOption(
                key="AMBOS",
                text="Cliente y proveedor",
            ),
        ],
    )

    credito_field = ft.TextField(
        label="Crédito predeterminado",
        hint_text="Ej: 30",
        suffix="días",
        value="0",
    )

    activo_field = ft.Checkbox(
        label="Empresa activa",
        value=True,
    )

    # =========================================================
    # CAMPO DE BÚSQUEDA
    # =========================================================

    buscar_field = ft.TextField(
        label="Buscar empresa",
        hint_text="Escriba nombre o RUC...",
    )

    informacion_resultados = ft.Text(
        "",
        size=13,
    )

    # =========================================================
    # MENSAJES DE ERROR
    # =========================================================

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

    email_error = ft.Text(
        "",
        color=ft.Colors.RED,
        visible=False,
    )

    tipo_error = ft.Text(
        "",
        color=ft.Colors.RED,
        visible=False,
    )

    credito_error = ft.Text(
        "",
        color=ft.Colors.RED,
        visible=False,
    )

    mensaje = ft.Text(
        "",
        size=14,
    )

    # =========================================================
    # CONTENEDOR DE RESULTADOS
    # =========================================================

    lista_empresas = ft.Column(
        spacing=10,
    )

    # =========================================================
    # LIMPIAR ERRORES
    # =========================================================

    def limpiar_errores():

        nombre_error.value = ""
        nombre_error.visible = False

        ruc_error.value = ""
        ruc_error.visible = False

        email_error.value = ""
        email_error.visible = False

        tipo_error.value = ""
        tipo_error.visible = False

        credito_error.value = ""
        credito_error.visible = False

        mensaje.value = ""

    # =========================================================
    # LIMPIAR FORMULARIO
    # =========================================================

    def limpiar_formulario():
        """
        Deja el formulario preparado para registrar
        una empresa nueva.
        """

        empresa_editando_id["valor"] = None

        nombre_field.value = ""
        ruc_field.value = ""
        direccion_field.value = ""
        email_field.value = ""

        tipo_field.value = "CLIENTE"

        credito_field.value = "0"

        activo_field.value = True

        boton_guardar.content = (
            "Guardar empresa"
        )

        boton_cancelar.visible = False

        limpiar_errores()

    # =========================================================
    # FILTRAR EMPRESAS EN MEMORIA
    # =========================================================

    def filtrar_empresas():
        """
        Busca dentro de empresas_cache.

        NO abre Excel.

        Devuelve:
        - resultados visibles
        - cantidad total de coincidencias
        """

        texto = normalizar_texto(
            buscar_field.value
        )

        # Ordenamos alfabéticamente.
        empresas_ordenadas = sorted(
            empresas_cache,
            key=lambda empresa:
                normalizar_texto(
                    empresa["nombre"]
                ),
        )

        # Si no hay búsqueda, todas son candidatas.
        if texto == "":
            coincidencias = (
                empresas_ordenadas
            )

        else:

            coincidencias_inicio = []
            coincidencias_parciales = []

            for empresa in empresas_ordenadas:

                nombre = normalizar_texto(
                    empresa["nombre"]
                )

                ruc = str(
                    empresa["ruc"]
                ).strip()

                # -----------------------------------------
                # PRIORIDAD 1
                # El nombre o RUC empieza con lo escrito.
                # -----------------------------------------

                if (
                    nombre.startswith(texto)
                    or ruc.startswith(texto)
                ):

                    coincidencias_inicio.append(
                        empresa
                    )

                # -----------------------------------------
                # PRIORIDAD 2
                # El texto aparece en otra posición.
                # -----------------------------------------

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

        total = len(
            coincidencias
        )

        resultados_visibles = (
            coincidencias[
                :LIMITE_RESULTADOS
            ]
        )

        return (
            resultados_visibles,
            total,
        )

    # =========================================================
    # CARGAR EMPRESA PARA EDITAR
    # =========================================================

    def cargar_empresa_para_editar(
        empresa,
    ):
        """
        Coloca los datos de una empresa existente
        en el formulario superior.
        """

        empresa_editando_id["valor"] = (
            empresa["id"]
        )

        nombre_field.value = (
            empresa["nombre"]
        )

        ruc_field.value = (
            empresa["ruc"]
        )

        direccion_field.value = (
            empresa["direccion"]
        )

        email_field.value = (
            empresa["email"]
        )

        tipo_field.value = (
            empresa["tipo"]
        )

        credito_field.value = str(
            empresa["credito_dias"]
        )

        activo_field.value = (
            empresa["activo"]
        )

        boton_guardar.content = (
            "Actualizar empresa"
        )

        boton_cancelar.visible = True

        mensaje.value = (
            "Editando empresa existente."
        )

        mensaje.color = ft.Colors.BLUE

        page.update()

    # =========================================================
    # CREAR TARJETA
    # =========================================================

    def crear_tarjeta_empresa(
        empresa,
    ):
        """
        Genera el elemento visual correspondiente
        a una empresa.
        """

        if empresa["activo"]:
            estado = "ACTIVA"
        else:
            estado = "INACTIVA"

        if empresa["credito_dias"] > 0:

            texto_credito = (
                f'{empresa["credito_dias"]} días'
            )

        else:

            texto_credito = (
                "No configurado"
            )

        controles = [
            ft.Text(
                empresa["nombre"],
                size=17,
                weight=ft.FontWeight.BOLD,
            ),
            ft.Text(
                f'RUC: {empresa["ruc"]}'
            ),
            ft.Text(
                f'Tipo: {empresa["tipo"]}'
            ),
            ft.Text(
                f'Crédito: {texto_credito}'
            ),
            ft.Text(
                f'Estado: {estado}'
            ),
        ]

        if empresa["direccion"]:

            controles.append(
                ft.Text(
                    f'Dirección: '
                    f'{empresa["direccion"]}'
                )
            )

        if empresa["email"]:

            controles.append(
                ft.Text(
                    f'Email: '
                    f'{empresa["email"]}'
                )
            )

        controles.append(
            ft.Button(
                content="Editar",
                on_click=(
                    lambda e, emp=empresa:
                    cargar_empresa_para_editar(
                        emp
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
    # REFRESCAR RESULTADOS
    # =========================================================

    def refrescar_empresas():
        """
        Actualiza únicamente los controles visuales.

        NO vuelve a abrir Excel.
        """

        lista_empresas.controls.clear()

        resultados, total = (
            filtrar_empresas()
        )

        # -----------------------------------------------------
        # INFORMACIÓN SOBRE RESULTADOS
        # -----------------------------------------------------

        if total == 0:

            informacion_resultados.value = (
                "No se encontraron empresas."
            )

            lista_empresas.controls.append(
                ft.Text(
                    "No existen resultados para esta búsqueda."
                )
            )

            return

        if total > LIMITE_RESULTADOS:

            informacion_resultados.value = (
                f"Mostrando "
                f"{LIMITE_RESULTADOS} "
                f"de {total} empresas. "
                f"Escriba para filtrar."
            )

        else:

            informacion_resultados.value = (
                f"{total} empresa(s) encontrada(s)."
            )

        # -----------------------------------------------------
        # CREAR SOLO LOS CONTROLES NECESARIOS
        # -----------------------------------------------------

        for empresa in resultados:

            lista_empresas.controls.append(
                crear_tarjeta_empresa(
                    empresa
                )
            )

    # =========================================================
    # EVENTO DE BÚSQUEDA
    # =========================================================

    def buscar_empresa(e):
        """
        Se ejecuta mientras el usuario escribe.

        La búsqueda ocurre exclusivamente
        sobre empresas_cache.
        """

        refrescar_empresas()

        page.update()

    buscar_field.on_change = (
        buscar_empresa
    )

    # =========================================================
    # GUARDAR / ACTUALIZAR
    # =========================================================

    def guardar_empresa(e):

        limpiar_errores()

        formulario_valido = True

        # -----------------------------------------------------
        # NOMBRE
        # -----------------------------------------------------

        valido, error = (
            validar_texto_obligatorio(
                nombre_field.value,
                "Nombre de empresa",
            )
        )

        if not valido:

            nombre_error.value = error
            nombre_error.visible = True

            formulario_valido = False

        # -----------------------------------------------------
        # RUC
        # -----------------------------------------------------

        valido, error = validar_ruc(
            ruc_field.value
        )

        if not valido:

            ruc_error.value = error
            ruc_error.visible = True

            formulario_valido = False

        # -----------------------------------------------------
        # EMAIL
        # -----------------------------------------------------

        valido, error = validar_email(
            email_field.value
        )

        if not valido:

            email_error.value = error
            email_error.visible = True

            formulario_valido = False

        # -----------------------------------------------------
        # TIPO
        # -----------------------------------------------------

        valido, error = (
            validar_tipo_empresa(
                tipo_field.value
            )
        )

        if not valido:

            tipo_error.value = error
            tipo_error.visible = True

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
        # DETENER SI EXISTEN ERRORES
        # -----------------------------------------------------

        if not formulario_valido:

            mensaje.value = (
                "Corrija los datos indicados."
            )

            mensaje.color = ft.Colors.RED

            page.update()
            return

        # =====================================================
        # CREAR O MODIFICAR
        # =====================================================

        empresa_id = (
            empresa_editando_id["valor"]
        )

        if empresa_id is None:

            guardado, resultado = (
                registrar_empresa(
                    nombre=nombre_field.value,
                    ruc=ruc_field.value,
                    direccion=direccion_field.value,
                    email=email_field.value,
                    tipo=tipo_field.value,
                    credito_dias=resultado_credito,
                    activo=activo_field.value,
                )
            )

        else:

            guardado, resultado = (
                actualizar_empresa(
                    empresa_id=empresa_id,
                    nombre=nombre_field.value,
                    ruc=ruc_field.value,
                    direccion=direccion_field.value,
                    email=email_field.value,
                    tipo=tipo_field.value,
                    credito_dias=resultado_credito,
                    activo=activo_field.value,
                )
            )

        # -----------------------------------------------------
        # ERROR AL GUARDAR
        # -----------------------------------------------------

        if not guardado:

            mensaje.value = resultado
            mensaje.color = ft.Colors.RED

            page.update()
            return

        # -----------------------------------------------------
        # ACTUALIZAR CACHÉ
        # -----------------------------------------------------

        recargar_cache()

        # Limpiar formulario.
        limpiar_formulario()

        mensaje.value = resultado
        mensaje.color = ft.Colors.GREEN

        # Actualizar resultados visuales.
        refrescar_empresas()

        page.update()

    # =========================================================
    # CANCELAR EDICIÓN
    # =========================================================

    def cancelar_edicion(e):

        limpiar_formulario()

        refrescar_empresas()

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
        content="Guardar empresa",
        on_click=guardar_empresa,
    )

    boton_cancelar = ft.Button(
        content="Cancelar edición",
        on_click=cancelar_edicion,
        visible=False,
    )

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
                "Registrar empresa",
                size=24,
                weight=ft.FontWeight.BOLD,
            ),
        ],
        spacing=15,
    )

    # =========================================================
    # FORMULARIO
    # =========================================================

    formulario = ft.ResponsiveRow(
        spacing=15,
        run_spacing=15,
        controls=[
            # -------------------------------------------------
            # NOMBRE
            # -------------------------------------------------

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

            # -------------------------------------------------
            # RUC
            # -------------------------------------------------

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
                    spacing=5,
                ),
            ),

            # -------------------------------------------------
            # DIRECCIÓN
            # -------------------------------------------------

            ft.Container(
                col={
                    "xs": 12,
                    "md": 6,
                },
                content=direccion_field,
            ),

            # -------------------------------------------------
            # EMAIL
            # -------------------------------------------------

            ft.Container(
                col={
                    "xs": 12,
                    "md": 6,
                },
                content=ft.Column(
                    controls=[
                        email_field,
                        email_error,
                    ],
                    spacing=5,
                ),
            ),

            # -------------------------------------------------
            # TIPO
            # -------------------------------------------------

            ft.Container(
                col={
                    "xs": 12,
                    "md": 6,
                },
                content=ft.Column(
                    controls=[
                        tipo_field,
                        tipo_error,
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
            # ACTIVO
            # -------------------------------------------------

            ft.Container(
                col={
                    "xs": 12,
                },
                content=activo_field,
            ),
        ],
    )

    # =========================================================
    # PRIMERA CARGA DE RESULTADOS
    # =========================================================

    refrescar_empresas()

    # =========================================================
    # MOSTRAR PANTALLA
    # =========================================================

    page.add(
        ft.SafeArea(
            content=ft.Column(
                controls=[
                    encabezado,

                    ft.Divider(),

                    ft.Text(
                        "Datos de la empresa",
                        size=18,
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
                        "Empresas registradas",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                    ),

                    buscar_field,

                    informacion_resultados,

                    lista_empresas,
                ],
                spacing=15,
            )
        )
    )