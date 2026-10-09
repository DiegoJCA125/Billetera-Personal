
import unittest

# Importamos la función que queremos comprobar.
from main import validar_movimiento


class TestValidarMovimiento(unittest.TestCase):
    """Pruebas automáticas para nuestra capa de calidad de datos."""

    def test_movimiento_valido(self):
        # Un movimiento correcto debe pasar la validación.
        resultado = validar_movimiento(
            "Gasto", "Comida", "Almuerzo", 25000
        )

        self.assertEqual(
            resultado,
            ("Gasto", "Comida", "Almuerzo", 25000.0)
        )

    def test_tipo_invalido(self):
        # No permitimos tipos diferentes de Ingreso o Gasto.
        with self.assertRaisesRegex(ValueError, "tipo de movimiento"):
            validar_movimiento("Compra", "Comida", "Almuerzo", 25000)

    def test_categoria_vacia(self):
        # Una categoría vacía debe rechazarse.
        with self.assertRaisesRegex(ValueError, "categoría es obligatoria"):
            validar_movimiento("Gasto", "   ", "Almuerzo", 25000)

    def test_categoria_demasiado_larga(self):
        # La categoría no puede superar los 100 caracteres.
        categoria_larga = "A" * 101

        with self.assertRaisesRegex(ValueError, "100 caracteres"):
            validar_movimiento("Gasto", categoria_larga, "Compra", 25000)

    def test_descripcion_vacia(self):
        # Una descripción vacía debe rechazarse.
        with self.assertRaisesRegex(ValueError, "descripción es obligatoria"):
            validar_movimiento("Gasto", "Comida", "   ", 25000)

    def test_monto_negativo(self):
        # No permitimos montos inferiores a cero.
        with self.assertRaisesRegex(ValueError, "no puede ser negativo"):
            validar_movimiento("Gasto", "Comida", "Almuerzo", -5000)

    def test_monto_no_numerico(self):
        # El monto debe poder convertirse a número.
        with self.assertRaisesRegex(ValueError, "número válido"):
            validar_movimiento("Gasto", "Comida", "Almuerzo", "abc")

    def test_monto_no_finito(self):
        # NaN no es un monto válido.
        with self.assertRaisesRegex(ValueError, "número finito"):
            validar_movimiento("Gasto", "Comida", "Almuerzo", float("nan"))

    def test_limpieza_de_espacios(self):
        # La función debe quitar espacios innecesarios.
        resultado = validar_movimiento(
            "Gasto", "  Comida  ", "  Almuerzo  ", 25000
        )

        self.assertEqual(
            resultado,
            ("Gasto", "Comida", "Almuerzo", 25000.0)
        )


# Permite ejecutar las pruebas directamente desde Python.
if __name__ == "__main__":
    unittest.main()
