from datetime import datetime
from decimal import Decimal, InvalidOperation
import re


# ============================================================
# TEXTO OBLIGATORIO
# ============================================================

def validar_texto_obligatorio(
    valor: str,
    nombre_campo: str,
):
    """
    Comprueba que un campo obligatorio tenga contenido.
    """

    if valor is None or valor.strip() == "":
        return (
            False,
            f"El campo '{nombre_campo}' es obligatorio.",
        )

    return True, ""


# ============================================================
# RUC
# ============================================================

def validar_ruc(ruc: str):
    """
    Realiza una validación estructural básica del RUC.

    Por ahora comprobamos:
    - que exista;
    - que solamente contenga números;
    - que tenga 13 dígitos.

    Más adelante podemos implementar la validación completa
    del RUC ecuatoriano según el tipo de contribuyente.
    """

    ruc = str(ruc or "").strip()

    if ruc == "":
        return (
            False,
            "El RUC es obligatorio.",
        )

    if not ruc.isdigit():
        return (
            False,
            "El RUC solo puede contener números.",
        )

    if len(ruc) != 13:
        return (
            False,
            "El RUC debe contener exactamente 13 dígitos.",
        )

    return True, ""


# ============================================================
# EMAIL
# ============================================================

def validar_email(email: str):
    """
    Comprueba la estructura básica de un correo electrónico.

    El correo será opcional.

    Si está vacío:
        válido.

    Si tiene contenido:
        debe tener una estructura similar a
        usuario@dominio.com
    """

    email = str(email or "").strip()

    # El email no será obligatorio.
    if email == "":
        return True, ""

    patron = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    if not re.match(patron, email):
        return (
            False,
            "Ingrese un correo electrónico válido.",
        )

    return True, ""


# ============================================================
# TIPO DE EMPRESA
# ============================================================

def validar_tipo_empresa(tipo: str):
    """
    Comprueba que el tipo pertenezca a los valores
    permitidos por el sistema.
    """

    tipos_validos = {
        "CLIENTE",
        "PROVEEDOR",
        "AMBOS",
    }

    tipo = str(tipo or "").strip().upper()

    if tipo not in tipos_validos:
        return (
            False,
            "Seleccione un tipo de empresa válido.",
        )

    return True, ""


# ============================================================
# CRÉDITO
# ============================================================

def validar_credito_dias(valor):
    """
    Comprueba que los días de crédito sean un número
    entero mayor o igual a cero.

    0 significa:
        sin crédito / pago inmediato / no aplica.
    """

    texto = str(
        valor if valor is not None else ""
    ).strip()

    if texto == "":
        return True, 0

    if not texto.isdigit():
        return (
            False,
            "Los días de crédito deben ser un número entero.",
        )

    dias = int(texto)

    if dias < 0:
        return (
            False,
            "Los días de crédito no pueden ser negativos.",
        )

    return True, dias


# ============================================================
# FECHA
# ============================================================

def validar_fecha(fecha: str):
    """
    Comprueba que la fecha tenga formato:

        dd/mm/aaaa

    y que represente una fecha real.
    """

    fecha = str(fecha or "").strip()

    if fecha == "":
        return (
            False,
            "La fecha de emisión es obligatoria.",
        )

    try:

        fecha_convertida = datetime.strptime(
            fecha,
            "%d/%m/%Y",
        )

        return (
            True,
            fecha_convertida,
        )

    except ValueError:

        return (
            False,
            "La fecha debe tener formato dd/mm/aaaa y ser válida.",
        )


# ============================================================
# TOTAL
# ============================================================

def validar_total(total: str):
    """
    Comprueba que el valor total sea numérico
    y mayor que cero.
    """

    total = str(total or "").strip()

    total = total.replace(
        ",",
        ".",
    )

    if total == "":
        return (
            False,
            "El valor total es obligatorio.",
        )

    try:

        valor = Decimal(
            total
        )

        if valor <= 0:
            return (
                False,
                "El valor total debe ser mayor que cero.",
            )

        return (
            True,
            valor,
        )

    except InvalidOperation:

        return (
            False,
            "El valor total debe ser numérico.",
        )