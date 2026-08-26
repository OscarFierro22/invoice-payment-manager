from datetime import datetime
from decimal import Decimal, InvalidOperation


def validar_texto_obligatorio(valor: str, nombre_campo: str):
    """
    Comprueba que un campo de texto no esté vacío.

    Retorna:
        (True, "") si el valor es válido.
        (False, "mensaje") si existe un error.
    """

    if valor is None or valor.strip() == "":
        return False, f"El campo '{nombre_campo}' es obligatorio."

    return True, ""


def validar_ruc(ruc: str):
    """
    Comprueba que el RUC tenga exactamente 13 dígitos.
    """

    ruc = ruc.strip()

    if ruc == "":
        return False, "El RUC es obligatorio."

    if not ruc.isdigit():
        return False, "El RUC solo puede contener números."

    if len(ruc) != 13:
        return False, "El RUC debe contener exactamente 13 dígitos."

    return True, ""


def validar_fecha(fecha: str):
    """
    Comprueba que la fecha tenga formato dd/mm/aaaas
    y que sea una fecha real.
    """

    fecha = fecha.strip()

    if fecha == "":
        return False, "La fecha de emisión es obligatoria."

    try:
        fecha_convertida = datetime.strptime(
            fecha,
            "%d/%m/%Y",
        )

        return True, fecha_convertida

    except ValueError:
        return (
            False,
            "La fecha debe tener formato dd/mm/aaaa y ser válida.",
        )


def validar_total(total: str):
    """
    Comprueba que el valor total sea un número positivo.
    Acepta punto o coma como separador decimal.
    """

    total = total.strip().replace(",", ".")

    if total == "":
        return False, "El valor total es obligatorio."

    try:
        valor = Decimal(total)

        if valor <= 0:
            return False, "El valor total debe ser mayor que cero."

        return True, valor

    except InvalidOperation:
        return False, "El valor total debe ser numérico."