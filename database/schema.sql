USE defaultdb;

CREATE TABLE IF NOT EXISTS clientes (
    id_cliente INT AUTO_INCREMENT,
    nombre VARCHAR(30) NOT NULL,
    apellido VARCHAR(30) NOT NULL,
    dni VARCHAR(10) NOT NULL UNIQUE,
    telefono VARCHAR(20),
    correo VARCHAR(100),
    activo BOOLEAN NOT NULL DEFAULT 1,
    PRIMARY KEY (id_cliente)
);

CREATE TABLE IF NOT EXISTS huespedes (
    id_huesped INT AUTO_INCREMENT,
    nombre VARCHAR(30) NOT NULL,
    apellido VARCHAR(30) NOT NULL,
    dni VARCHAR(10) NOT NULL UNIQUE,
    telefono VARCHAR(20),
    activo BOOLEAN NOT NULL DEFAULT 1,
    PRIMARY KEY (id_huesped)
);

CREATE TABLE IF NOT EXISTS habitaciones (
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

CREATE TABLE IF NOT EXISTS reservas (
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

-- Las tablas intermedias quedan sin el campo activo, tal como pediste
CREATE TABLE IF NOT EXISTS reservas_x_huespedes (
    id_res_x_hue INT AUTO_INCREMENT,
    id_reserva INT NOT NULL,
    id_huesped INT NOT NULL,
    PRIMARY KEY (id_res_x_hue),
    UNIQUE (id_reserva, id_huesped),
    FOREIGN KEY (id_reserva) REFERENCES reservas (id_reserva),
    FOREIGN KEY (id_huesped) REFERENCES huespedes (id_huesped)
);

CREATE TABLE IF NOT EXISTS reservas_x_habitaciones (
    id_res_x_hab INT AUTO_INCREMENT,
    id_reserva INT NOT NULL,
    id_habitacion INT NOT NULL,
    PRIMARY KEY (id_res_x_hab),
    UNIQUE (id_reserva, id_habitacion),
    FOREIGN KEY (id_reserva) REFERENCES reservas (id_reserva),
    FOREIGN KEY (id_habitacion) REFERENCES habitaciones (id_habitacion)
);