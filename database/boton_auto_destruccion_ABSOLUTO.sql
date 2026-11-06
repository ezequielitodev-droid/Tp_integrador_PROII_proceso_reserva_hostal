-- 1. Desactivar temporalmente la verificación de claves foráneas para evitar bloqueos al hacer DROP
SET FOREIGN_KEY_CHECKS = 0;

-- 2. Eliminar las tablas si ya existen (orden inverso de dependencia)
DROP TABLE IF EXISTS reservas_x_habitaciones;
DROP TABLE IF EXISTS reservas_x_huespedes;
DROP TABLE IF EXISTS reservas;
DROP TABLE IF EXISTS habitaciones;
DROP TABLE IF EXISTS huespedes;
DROP TABLE IF EXISTS clientes;

-- 3. Volver a activar las restricciones de claves foráneas
SET FOREIGN_KEY_CHECKS = 1;

-- 4. Crear todo el esquema desde cero con el campo 'activo' incorporado

CREATE TABLE clientes (
    id_cliente INT AUTO_INCREMENT,
    nombre VARCHAR(30) NOT NULL,
    apellido VARCHAR(30) NOT NULL,
    dni VARCHAR(10) NOT NULL UNIQUE,
    telefono VARCHAR(20),
    correo VARCHAR(100),
    activo BOOLEAN NOT NULL DEFAULT 1,
    PRIMARY KEY (id_cliente)
);

CREATE TABLE huespedes (
    id_huesped INT AUTO_INCREMENT,
    nombre VARCHAR(30) NOT NULL,
    apellido VARCHAR(30) NOT NULL,
    dni VARCHAR(10) NOT NULL UNIQUE,
    telefono VARCHAR(20),
    activo BOOLEAN NOT NULL DEFAULT 1,
    PRIMARY KEY (id_huesped)
);

CREATE TABLE habitaciones (
    id_habitacion INT AUTO_INCREMENT,
    numero INT NOT NULL UNIQUE,
    capacidad INT NOT NULL,
    precio_noche DECIMAL(10, 2) NOT NULL,
    estado ENUM('DISPONIBLE', 'OCUPADA') NOT NULL DEFAULT 'DISPONIBLE',
    activo BOOLEAN NOT NULL DEFAULT 1,
    PRIMARY KEY (id_habitacion),
    CHECK (capacidad > 0),
    CHECK (precio_noche >= 0)
);

CREATE TABLE reservas (
    id_reserva INT AUTO_INCREMENT,
    fecha_reserva DATE NOT NULL,
    fecha_ingreso DATE NOT NULL,
    fecha_salida DATE NOT NULL,
    estado ENUM('RESERVADA', 'CANCELADA') NOT NULL DEFAULT 'RESERVADA',
    monto_total DECIMAL(10, 2) NOT NULL DEFAULT 0,
    id_cliente INT NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT 1,
    PRIMARY KEY (id_reserva),
    FOREIGN KEY (id_cliente) REFERENCES clientes (id_cliente),
    CHECK (fecha_salida > fecha_ingreso)
);

CREATE TABLE reservas_x_huespedes (
    id_res_x_hue INT AUTO_INCREMENT,
    id_reserva INT NOT NULL,
    id_huesped INT NOT NULL,
    PRIMARY KEY (id_res_x_hue),
    UNIQUE (id_reserva, id_huesped),
    FOREIGN KEY (id_reserva) REFERENCES reservas (id_reserva),
    FOREIGN KEY (id_huesped) REFERENCES huespedes (id_huesped)
);

CREATE TABLE reservas_x_habitaciones (
    id_res_x_hab INT AUTO_INCREMENT,
    id_reserva INT NOT NULL,
    id_habitacion INT NOT NULL,
    PRIMARY KEY (id_res_x_hab),
    UNIQUE (id_reserva, id_habitacion),
    FOREIGN KEY (id_reserva) REFERENCES reservas (id_reserva),
    FOREIGN KEY (id_habitacion) REFERENCES habitaciones (id_habitacion)
);