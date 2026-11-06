#Imports:
import logging

from db_connection import obtener_conexion
from models.cliente import Cliente

#Global Variables:

logger = logging.getLogger(__name__)

#Constants:

#Class:

class ClienteDAO:

    #Methods: 

    def crear_cliente(self, cliente: Cliente) -> int | None:

        conexion = None
        cursor = None

        try:

            conexion = obtener_conexion()
            cursor = conexion.cursor()

            instruccion_sql = ""#Instruccion SQL correspondiente

            valores = (
                cliente.get_nombre(),
                cliente.get_apellido(),
                cliente.get_dni(),
                cliente.get_telefono(),
                cliente.get_correo(),
                cliente.get_activo()
            )

            cursor.execute(instruccion_sql, valores)
            conexion.commit()

            id_generado = cursor.lastrowid

            logging.info(f"Cliente creado exitosamente con ID: {id_generado}")

            return id_generado

        except Exception as e:

            logging.error(f"Error al crear el cliente: {e}")

            if conexion:
                conexion.rollback()

            return None

        finally:

            if cursor:
                cursor.close()
            if conexion and conexion.is_connected():
                conexion.close()

    def obtener_clientes(self) -> list[Cliente | None]:

        conexion = None
        cursor = None

        list_clientes = []

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            instruccion_sql = ""#Instruccion
            
            cursor.execute(instruccion_sql)
            resultados = cursor.fetchall()

            for registro in resultados:

                cliente = Cliente(
                    id_cliente=registro[0],  # type: ignore
                    nombre=registro[1],      # type: ignore
                    apellido=registro[2],    # type: ignore
                    dni=registro[3],         # type: ignore
                    telefono=registro[4],    # type: ignore
                    correo=registro[5],      # type: ignore
                    activo=bool(registro[6]) # type: ignore
                )

                list_clientes.append(cliente)

            logging.info(f"Se obtuvieron {len(list_clientes)} clientes exitosamente.")

            return list_clientes
            
        except Exception as e: 

            logging.error(f"Error al obtener los clientes: {e}")
            return []

        finally:

            if cursor:
                cursor.close()
            if conexion and conexion.is_connected():
                conexion.close()

    def obtener_cliente_por_id(self, id_cliente: int) -> Cliente | None:

        conexion = None
        cursor = None

        try:

            conexion = obtener_conexion()
            cursor = conexion.cursor()

            instruccion_sql = ""#Instruccion SQL
            
            valor = (id_cliente, )

            cursor.execute(instruccion_sql, valor)
            resultado = cursor.fetchone()

            if not resultado:

                logging.warning(f"No se encontró ningún cliente con el ID: {id_cliente}")

                return None

            cliente = Cliente(
                id_cliente=resultado[0],  # type: ignore
                nombre=resultado[1],      # type: ignore
                apellido=resultado[2],    # type: ignore
                dni=resultado[3],         # type: ignore
                telefono=resultado[4],    # type: ignore
                correo=resultado[5],      # type: ignore
                activo=bool(resultado[6]) # type: ignore
            )

            logging.info(f"Cliente con ID {id_cliente} obtenido exitosamente.")

            return cliente

        except Exception as e:

            logging.error(f"Error al obtener el cliente por ID: {e}")

            return None

        finally:

            if cursor:
                cursor.close()
            if conexion and conexion.is_connected():
                conexion.close()

    def modificar_cliente(
            self, 
            id_cliente: int, 
            nombre: str | None = None, 
            apellido: str | None = None, 
            dni: str | None = None, 
            telefono: str | None = None, 
            correo: str | None = None,
            activo: bool | None = None
    ) -> Cliente | None:

        conexion = None
        cursor = None

        try:

            conexion = obtener_conexion()
            cursor = conexion.cursor()

            instruccion_sql = ""#Instruccion SQL

            valores = (nombre, apellido, dni, telefono, correo, activo, id_cliente)

            cursor.execute(instruccion_sql, valores)
            conexion.commit()

            if cursor.rowcount == 0:

                logging.warning(f"No se encontró ningún cliente con el ID: {id_cliente} para modificar.")

                return None

            logging.info(f"Cliente con ID {id_cliente} modificado exitosamente.")
            
            return self.obtener_cliente_por_id(id_cliente)

        except Exception as e:

            logging.error(f"Error al modificar el cliente: {e}")

            if conexion: conexion.rollback()

            return None

        finally:

            if cursor:
                cursor.close()

            if conexion and conexion.is_connected():
                conexion.close()
    
    def eliminar_cliente(self, id_cliente: int) -> bool:
        
        """
            Realiza una baja lógica del cliente cambiando su estado 'activo' a False,
            preservando el historial de reservas y la integridad de la base de datos.
        """
        try:
            
            cliente_modificado = self.modificar_cliente(
                id_cliente=id_cliente, 
                activo=False
            )

            if cliente_modificado is None:

                logging.warning(f"No se encontró ningún cliente con el ID: {id_cliente} para dar de baja.")

                return False

            logging.info(f"Cliente con ID {id_cliente} dado de baja lógica (activo = False) exitosamente.")

            return True

        except Exception as e:

            logging.error(f"Error crítico al intentar dar de baja al cliente con ID {id_cliente}: {e}")
            
            return False