from pathlib import Path

from openpyxl import Workbook, load_workbook


# ---------------------------------------------------------
# RUTAS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

EXCEL_PATH = DATA_DIR / "Control_Electropart.xlsx"

HOJA_EMPRESAS = "Empresas"


# ---------------------------------------------------------
# INICIALIZACIÓN
# ---------------------------------------------------------

def inicializar_archivo():
    """
    Crea el archivo Excel y la hoja Empresas si todavía
    no existen.
    """

    # Crear carpeta data/ si no existe.
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Si el archivo Excel todavía no existe.
    if not EXCEL_PATH.exists():

        workbook = Workbook()

        hoja = workbook.active
        hoja.title = HOJA_EMPRESAS

        hoja.append(
            [
                "ID",
                "Nombre",
                "RUC",
            ]
        )

        workbook.save(EXCEL_PATH)
        workbook.close()

        return

    # El archivo existe, pero comprobamos
    # que también exista la hoja Empresas.
    workbook = load_workbook(EXCEL_PATH)

    if HOJA_EMPRESAS not in workbook.sheetnames:

        hoja = workbook.create_sheet(
            HOJA_EMPRESAS
        )

        hoja.append(
            [
                "ID",
                "Nombre",
                "RUC",
            ]
        )

        workbook.save(EXCEL_PATH)

    workbook.close()


# ---------------------------------------------------------
# LISTAR EMPRESAS
# ---------------------------------------------------------

def listar_empresas():
    """
    Devuelve todas las empresas almacenadas en Excel.

    Cada empresa se devuelve como diccionario:

    {
        "id": 1,
        "nombre": "Hotel Ejemplo",
        "ruc": "179..."
    }
    """

    inicializar_archivo()

    workbook = load_workbook(EXCEL_PATH)

    hoja = workbook[HOJA_EMPRESAS]

    empresas = []

    for fila in hoja.iter_rows(
        min_row=2,
        values_only=True,
    ):

        empresa_id = fila[0]
        nombre = fila[1]
        ruc = fila[2]

        if nombre is None or ruc is None:
            continue

        empresas.append(
            {
                "id": empresa_id,
                "nombre": str(nombre).strip(),
                "ruc": str(ruc).strip(),
            }
        )

    workbook.close()

    return empresas


# ---------------------------------------------------------
# BUSCAR
# ---------------------------------------------------------
def buscar_empresas(texto, campo=None, limite=8):
    """
    Busca empresas registradas.

    campo puede ser:
        "nombre" -> busca únicamente por nombre.
        "ruc"    -> busca únicamente por RUC.
        None     -> busca por ambos campos.
    """

    texto = (texto or "").strip().lower()

    if texto == "":
        return []

    empresas = listar_empresas()

    resultados = []

    for empresa in empresas:
        nombre = empresa["nombre"].lower()
        ruc = empresa["ruc"].lower()

        coincide = False

        if campo == "nombre":
            coincide = texto in nombre

        elif campo == "ruc":
            coincide = texto in ruc

        else:
            coincide = (
                texto in nombre
                or texto in ruc
            )

        if coincide:
            resultados.append(empresa)

        if len(resultados) >= limite:
            break

    return resultados
# ---------------------------------------------------------
# BUSCAR POR RUC
# ---------------------------------------------------------

def obtener_empresa_por_ruc(ruc):
    """
    Devuelve una empresa según su RUC.
    """

    ruc = (ruc or "").strip()

    for empresa in listar_empresas():

        if empresa["ruc"] == ruc:
            return empresa

    return None


# ---------------------------------------------------------
# REGISTRAR
# ---------------------------------------------------------

def registrar_empresa(nombre, ruc):
    """
    Registra una nueva empresa en el Excel.

    Retorna:
        (True, mensaje)
        (False, mensaje)
    """

    nombre = (nombre or "").strip()
    ruc = (ruc or "").strip()

    inicializar_archivo()

    workbook = load_workbook(EXCEL_PATH)

    hoja = workbook[HOJA_EMPRESAS]

    # -----------------------------------------------------
    # COMPROBAR DUPLICADOS
    # -----------------------------------------------------

    for fila in hoja.iter_rows(
        min_row=2,
        values_only=True,
    ):

        nombre_existente = str(
            fila[1] or ""
        ).strip()

        ruc_existente = str(
            fila[2] or ""
        ).strip()

        if ruc_existente == ruc:

            workbook.close()

            return (
                False,
                "Ya existe una empresa registrada con este RUC.",
            )

        if nombre_existente.lower() == nombre.lower():

            workbook.close()

            return (
                False,
                "Ya existe una empresa registrada con este nombre.",
            )

    # -----------------------------------------------------
    # GENERAR ID
    # -----------------------------------------------------

    ids = []

    for fila in hoja.iter_rows(
        min_row=2,
        values_only=True,
    ):

        if isinstance(fila[0], int):
            ids.append(fila[0])

    nuevo_id = max(
        ids,
        default=0,
    ) + 1

    # -----------------------------------------------------
    # GUARDAR
    # -----------------------------------------------------

    hoja.append(
        [
            nuevo_id,
            nombre,
            ruc,
        ]
    )

    workbook.save(EXCEL_PATH)
    workbook.close()

    return (
        True,
        "Empresa registrada correctamente.",
    )