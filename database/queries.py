#Archivo donde guardamos las instrucciones SQL necesarias...

#INSTRUCCIONES DE PATRONES DAO (CRUDs):

#Instrucciones de Cliente:----------------------------
instruccion_crear_cliente = """
INSERT INTO clientes( 
        nombre, 
        apellido, 
        dni, 
        telefono, 
        correo,
        activo
    )
VALUES(%s, %s, %s, %s, %s, %s) 
"""

instruccion_obtener_clientes = """
SELECT id_cliente, nombre, apellido, dni, telefono, correo, activo 
FROM clientes
"""

instruccion_obtener_cliente_por_id = """
SELECT id_cliente, nombre, apellido, dni, telefono, correo, activo 
FROM clientes 
WHERE id_cliente = %s
"""

instruccion_modificar_cliente = """
UPDATE clientes SET
        nombre = COALESCE(%s, nombre),
        apellido = COALESCE(%s, apellido),
        dni = COALESCE(%s, dni),
        telefono = COALESCE(%s, telefono),
        correo = COALESCE(%s, correo),
        activo = COALESCE(%s, activo)
WHERE id_cliente = %s
"""

# Baja lógica en lugar de DELETE físico, No la usamos porque usamos la instruccion del modificar con los parametros convenientes... Lo mismo en todos los otros modelos
instruccion_eliminar_cliente = """
UPDATE clientes 
SET activo = 0 
WHERE id_cliente = %s
"""

#Instrucciones de Cliente:----------------------------

#Instrucciones de Huespedes----------------------------

instruccion_crear_huesped = """
INSERT INTO huespedes( 
        nombre, 
        apellido, 
        dni, 
        telefono,
        activo
    )
VALUES(%s, %s, %s, %s, %s) 
"""

instruccion_obtener_huesped = """
SELECT id_huesped, nombre, apellido, dni, telefono, activo 
FROM huespedes
"""

instruccion_obtener_huesped_por_id = """
SELECT id_huesped, nombre, apellido, dni, telefono, activo 
FROM huespedes
WHERE id_huesped = %s
"""

instruccion_modificar_huesped = """
UPDATE huespedes SET
        nombre = COALESCE(%s, nombre),
        apellido = COALESCE(%s, apellido),
        dni = COALESCE(%s, dni),
        telefono = COALESCE(%s, telefono),
        activo = COALESCE(%s, activo)
WHERE id_huesped = %s
"""

instruccion_eliminar_huesped = """
UPDATE huespedes 
SET activo = 0 
WHERE id_huesped = %s
"""

#Instrucciones de Huespedes----------------------------

#Instrucciones de Habitaciones------------------------

instruccion_crear_habitacion = """
INSERT INTO habitaciones( 
        numero, 
        capacidad, 
        precio_noche, 
        estado,
        activo
    )
VALUES(%s, %s, %s, %s, %s) 
"""

instruccion_obtener_habitacion = """
SELECT id_habitacion, numero, capacidad, precio_noche, estado, activo 
FROM habitaciones
"""

instruccion_obtener_habitacion_por_id = """
SELECT id_habitacion, numero, capacidad, precio_noche, estado, activo 
FROM habitaciones
WHERE id_habitacion = %s
"""

instruccion_modificar_habitacion = """
UPDATE habitaciones SET
        numero = COALESCE(%s, numero),
        capacidad = COALESCE(%s, capacidad),
        precio_noche = COALESCE(%s, precio_noche),
        estado = COALESCE(%s, estado),
        activo = COALESCE(%s, activo)
WHERE id_habitacion = %s
"""

instruccion_eliminar_habitacion = """
UPDATE habitaciones 
SET activo = 0 
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
        monto_total,
        id_cliente,
        activo
    )
VALUES(%s, %s, %s, %s, %s, %s, %s) 
"""

instruccion_obtener_reserva = """
SELECT id_reserva, fecha_reserva, fecha_ingreso, fecha_salida, estado, monto_total, id_cliente, activo 
FROM reservas
"""

instruccion_obtener_reserva_por_id = """
SELECT id_reserva, fecha_reserva, fecha_ingreso, fecha_salida, estado, monto_total, id_cliente, activo 
FROM reservas
WHERE id_reserva = %s
"""

instruccion_modificar_reserva = """
UPDATE reservas SET
        fecha_reserva = COALESCE(%s, fecha_reserva),
        fecha_ingreso = COALESCE(%s, fecha_ingreso),
        fecha_salida = COALESCE(%s, fecha_salida),
        estado = COALESCE(%s, estado),
        monto_total = COALESCE(%s, monto_total),
        id_cliente = COALESCE(%s, id_cliente),
        activo = COALESCE(%s, activo)
WHERE id_reserva = %s
"""

instruccion_eliminar_reserva = """
UPDATE reservas 
SET activo = 0 
WHERE id_reserva = %s
"""

#Instrucciones de Reservas----------------------------