DELETE FROM reservas_x_habitaciones;
DELETE FROM reservas_x_huespedes;
DELETE FROM reservas;
DELETE FROM habitaciones;
DELETE FROM huespedes;
DELETE FROM clientes;

ALTER TABLE reservas_x_habitaciones AUTO_INCREMENT = 1;
ALTER TABLE reservas_x_huespedes AUTO_INCREMENT = 1;
ALTER TABLE reservas AUTO_INCREMENT = 1;
ALTER TABLE habitaciones AUTO_INCREMENT = 1;
ALTER TABLE huespedes AUTO_INCREMENT = 1;
ALTER TABLE clientes AUTO_INCREMENT = 1;

INSERT INTO clientes (nombre, apellido, dni, telefono, correo) VALUES
('Martín', 'Gómez', '30123456', '387-4112233', 'martin.gomez@example.com'),
('Sofía', 'Álvarez', '28456789', '387-4556677', 'sofia.alvarez@example.com'),
('Carolina', 'Méndez', '32789012', '387-4223344', 'carolina.mendez@example.com'),
('Diego', 'Herrera', '35123987', '387-4334455', 'diego.herrera@example.com'),
('Florencia', 'Rojas', '33456123', '387-4445566', 'florencia.rojas@example.com'),
('Nicolás', 'Vega', '31987654', '387-4667788', 'nicolas.vega@example.com'),
('Agustina', 'Paz', '36234567', '387-4778899', 'agustina.paz@example.com'),
('Ramiro', 'Castro', '34567890', '387-4889900', 'ramiro.castro@example.com');

INSERT INTO huespedes (nombre, apellido, dni, telefono) VALUES
('Lucía', 'Pérez', '40111222', '387-4001122'),
('Tomás', 'Ruiz', '41222333', '387-4002233'),
('Camila', 'Díaz', '42333444', '387-4003344'),
('Julián', 'Torres', '39444555', '387-4004455'),
('Valentina', 'Cruz', '38555666', '387-4005566'),
('Mateo', 'Silva', '37666777', '387-4006677'),
('Isabella', 'Romero', '43111000', '387-4007788'),
('Santiago', 'Flores', '43222111', '387-4008899'),
('Martina', 'Acosta', '42444222', '387-4009900'),
('Benjamín', 'Medina', '41555333', '387-4010011'),
('Emma', 'Sosa', '40666444', '387-4011122'),
('Lautaro', 'Núñez', '39777555', '387-4012233'),
('Catalina', 'Ríos', '38888666', '387-4013344'),
('Joaquín', 'Benítez', '37999777', '387-4014455'),
('Mía', 'Ortiz', '44000888', '387-4015566'),
('Thiago', 'Molina', '44111999', '387-4016677'),
('Olivia', 'Castro', '43555000', '387-4017788'),
('Felipe', 'Ibarra', '42666111', '387-4018899'),
('Renata', 'Luna', '41777222', '387-4019900'),
('Bruno', 'Aguirre', '40888333', '387-4020011');

INSERT INTO habitaciones (numero, capacidad, precio_noche, estado) VALUES
(101, 4, 18000.00, 'DISPONIBLE'),
(102, 4, 18000.00, 'DISPONIBLE'),
(103, 6, 15000.00, 'DISPONIBLE'),
(104, 8, 12000.00, 'DISPONIBLE'),
(201, 2, 25000.00, 'DISPONIBLE'),
(202, 2, 25000.00, 'OCUPADA'),
(203, 3, 22000.00, 'DISPONIBLE'),
(204, 2, 28000.00, 'OCUPADA'),
(301, 4, 20000.00, 'DISPONIBLE'),
(302, 6, 16000.00, 'OCUPADA');

INSERT INTO reservas (fecha_reserva, fecha_ingreso, fecha_salida, estado, monto_total, id_cliente) VALUES
('2026-09-01', '2026-09-10', '2026-09-13', 'RESERVADA', 54000.00, 1),
('2026-09-05', '2026-09-15', '2026-09-18', 'RESERVADA', 75000.00, 2),
('2026-09-12', '2026-09-20', '2026-09-22', 'RESERVADA', 30000.00, 3),
('2026-09-18', '2026-09-28', '2026-10-01', 'RESERVADA', 120000.00, 4),
('2026-09-25', '2026-10-05', '2026-10-08', 'RESERVADA', 36000.00, 5),
('2026-09-30', '2026-10-10', '2026-10-12', 'RESERVADA', 40000.00, 6),
('2026-10-02', '2026-10-12', '2026-10-15', 'CANCELADA', 54000.00, 1),
('2026-10-08', '2026-10-18', '2026-10-21', 'RESERVADA', 81000.00, 7),
('2026-10-15', '2026-10-22', '2026-10-25', 'RESERVADA', 75000.00, 3),
('2026-10-20', '2026-10-26', '2026-10-28', 'RESERVADA', 44000.00, 8),
('2026-10-24', '2026-10-30', '2026-11-02', 'RESERVADA', 60000.00, 2),
('2026-10-28', '2026-11-01', '2026-11-05', 'RESERVADA', 100000.00, 4),
('2026-10-29', '2026-11-01', '2026-11-04', 'RESERVADA', 48000.00, 5),
('2026-11-01', '2026-11-10', '2026-11-13', 'RESERVADA', 108000.00, 6),
('2026-11-02', '2026-11-15', '2026-11-17', 'RESERVADA', 94000.00, 7),
('2026-11-02', '2026-11-20', '2026-11-24', 'CANCELADA', 60000.00, 8),
('2026-11-03', '2026-11-25', '2026-11-28', 'RESERVADA', 36000.00, 1);

INSERT INTO reservas_x_habitaciones (id_reserva, id_habitacion) VALUES
(1, 1), (2, 5), (3, 3), (4, 2), (4, 7), (5, 4), (6, 9), (7, 1), (8, 3), (8, 4),
(9, 5), (10, 7), (11, 9), (12, 6), (13, 10), (14, 1), (14, 2), (15, 5), (15, 7),
(16, 3), (17, 4);

INSERT INTO reservas_x_huespedes (id_reserva, id_huesped) VALUES
(1, 1), (1, 2), (1, 3),
(2, 4), (2, 5),
(3, 6), (3, 7), (3, 8),
(4, 9), (4, 10), (4, 11), (4, 12),
(5, 13), (5, 14), (5, 15), (5, 16),
(6, 17), (6, 18),
(7, 1), (7, 2),
(8, 6), (8, 7), (8, 8), (8, 19), (8, 20),
(9, 4), (9, 5),
(10, 12), (10, 15),
(11, 9), (11, 10),
(12, 11), (12, 12),
(13, 13), (13, 14), (13, 15), (13, 16),
(14, 17), (14, 18), (14, 19), (14, 20),
(15, 1), (15, 2), (15, 3), (15, 4),
(16, 5), (16, 6),
(17, 7), (17, 8), (17, 9);