#Archivo donde guardamos las instrucciones SQL necesarias...

#INSTRUCCIONES DE PATRONES DAO (CRUDs):

#Instrucciones de Cliente:----------------------------
instruccion_crear_cliente = """
INSERT INTO clientes( 
        nombre, 
        apellido, 
        dni, 
        telefono, 
        correo
    )
VALUES(%s, %s, %s, %s, %s) 
"""

instruccion_obtener_clientes = """
SELECT * FROM clientes
"""

instruccion_obtener_cliente_por_id = """
SELECT * FROM clientes 
WHERE id_cliente = %s
"""

instruccion_modificar_cliente = """
UPDATE clientes SET
        nombre = %s,
        apellido = %s,
        dni = %s,
        telefono = %s,
        correo = %s
WHERE id_cliente = %s
"""

instruccion_eliminar_cliente = """
DELETE FROM clientes 
WHERE id_cliente = %s
"""

#Instrucciones de Cliente:----------------------------

#Instrucciones de Huepedes----------------------------

instruccion_crear_huesped = """
INSERT INTO huespedes( 
        nombre, 
        apellido, 
        dni, 
        telefono, 
    )
VALUES(%s, %s, %s, %s) 
"""

instruccion_obtener_huesped = """
SELECT * FROM huespedes
"""

instruccion_obtener_huesped_por_id = """
SELECT * FROM huespedes
WHERE id_huesped = %s
"""

instruccion_modificar_huesped = """
UPDATE huespedes SET
        nombre = %s,
        apellido = %s,
        dni = %s,
        telefono = %s,
WHERE id_huesped = %s
"""

instruccion_eliminar_huesped = """
DELETE FROM huespedes 
WHERE id_huesped = %s
"""

#Instrucciones de Huepedes----------------------------

#Instrucciones de Habitaciones------------------------

instruccion_crear_habitacion = """
INSERT INTO habitaciones( 
        numero, 
        capacidad, 
        precio_noche, 
        estado, 
    )
VALUES(%s, %s, %s, %s) 
"""

instruccion_obtener_habitacion = """
SELECT * FROM habitaciones
"""

instruccion_obtener_habitacion_por_id = """
SELECT * FROM habitaciones
WHERE id_habitacion = %s
"""

instruccion_modificar_habitacion = """
UPDATE habitaciones SET
        numero = %s,
        capacidad = %s,
        precio_noche = %s,
        estado = %s,
WHERE id_habitacion = %s
"""

instruccion_eliminar_habitacion = """
DELETE FROM habitaciones
WHERE id_habitacion = %s
"""

#Instrucciones de Habitaciones------------------------

#Instrucciones de Reservas----------------------------

instruccion_crear_reserva = """
INSERT INTO reservas( 
        fecha_reserva, 
        fecha_ingreso, 
        fecha_salida, 
        estado, 
        monto_total
        id_cliente 
    )
VALUES(%s, %s, %s, %s, %s, %s) 
"""

instruccion_obtener_reserva = """
SELECT * FROM reservas
"""

instruccion_obtener_reserva_por_id = """
SELECT * FROM reservas
WHERE id_reserva = %s
"""

instruccion_modificar_reserva = """
UPDATE reservas SET
        fecha_reserva, 
        fecha_ingreso, 
        fecha_salida, 
        estado, 
        monto_total
        id_cliente 
WHERE id_reverva = %s
"""

instruccion_eliminar_reserva = """
DELETE FROM reservas
WHERE id_reserva = %s
"""

#Instrucciones de Reservas----------------------------