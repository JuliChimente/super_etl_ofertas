from src.services.rds import RDS


class Supermercado:
    def __init__(self, supermercado: str, categorias: list):
        self.supermercado = supermercado
        self.categorias = categorias
        self.lista_productos = []

    def cargar_productos_a_db(self):
        rds = RDS()

        # Ejecutar una consulta para insertar los productos en la tabla
        consulta = 'INSERT INTO productos (supermercado, nombre_producto, precio_producto, promocion_producto, url_producto) VALUES '

        for producto in self.lista_productos:
            consulta += str(
                (producto['supermercado'], producto['nombre'], producto['precio'], producto['promo'], producto['url']))
        rds.execute_query(consulta)
        rds.disconnect()
