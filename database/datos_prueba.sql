-- Limpieza de tablas respetando el orden de las llaves foráneas y reinicio de IDs
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

-- =========================================================================
-- 20 CLIENTES TITULARES DE PRUEBA
-- =========================================================================
INSERT INTO clientes (nombre, apellido, dni, telefono, correo) VALUES
('Martín', 'Gómez', '30123456', '387-4112233', 'martin.gomez@example.com'),
('Sofía', 'Álvarez', '28456789', '387-4556677', 'sofia.alvarez@example.com'),
('Carolina', 'Méndez', '32789012', '387-4223344', 'carolina.mendez@example.com'),
('Diego', 'Herrera', '35123987', '387-4334455', 'diego.herrera@example.com'),
('Florencia', 'Rojas', '33456123', '387-4445566', 'florencia.rojas@example.com'),
('Nicolás', 'Vega', '31987654', '387-4667788', 'nicolas.vega@example.com'),
('Agustina', 'Paz', '36234567', '387-4778899', 'agustina.paz@example.com'),
('Ramiro', 'Castro', '34567890', '387-4889900', 'ramiro.castro@example.com'),
('Valeria', 'Suárez', '37890123', '387-4990011', 'valeria.suarez@example.com'),
('Matías', 'Navarro', '38901234', '387-4111222', 'matias.navarro@example.com'),
('Luciana', 'Benítez', '39012345', '387-4222333', 'luciana.benitez@example.com'),
('Facundo', 'Giménez', '40123456', '387-4333444', 'facundo.gimenez@example.com'),
('Camila', 'Medina', '41234567', '387-4444555', 'camila.medina@example.com'),
('Gonzalo', 'Peralta', '42345678', '387-4555666', 'gonzalo.peralta@example.com'),
('Agustín', 'Acosta', '43456789', '387-4666777', 'agustin.acosta@example.com'),
('Julieta', 'Molina', '44567890', '387-4777888', 'julieta.molina@example.com'),
('Lucas', 'Silva', '45678901', '387-4888999', 'lucas.silva@example.com'),
('Mariana', 'Ortiz', '46789012', '387-4999000', 'mariana.ortiz@example.com'),
('Esteban', 'Romero', '47890123', '387-4000111', 'esteban.romero@example.com'),
('Natalia', 'Díaz', '48901234', '387-4001222', 'natalia.diaz@example.com');


-- =========================================================================
-- 60 HABITACIONES (Numeradas del 1 al 60 con capacidades rotativas de 1 a 4)
-- =========================================================================
INSERT INTO habitaciones (numero, capacidad, precio_noche, estado) VALUES
(1, 4, 18000.00, 'DISPONIBLE'), (2, 4, 18000.00, 'DISPONIBLE'), (3, 2, 15000.00, 'DISPONIBLE'), (4, 1, 12000.00, 'DISPONIBLE'),
(5, 3, 20000.00, 'DISPONIBLE'), (6, 2, 15000.00, 'DISPONIBLE'), (7, 4, 18000.00, 'DISPONIBLE'), (8, 1, 12000.00, 'DISPONIBLE'),
(9, 3, 20000.00, 'DISPONIBLE'), (10, 2, 15000.00, 'DISPONIBLE'), (11, 4, 18000.00, 'DISPONIBLE'), (12, 1, 12000.00, 'DISPONIBLE'),
(13, 2, 15000.00, 'DISPONIBLE'), (14, 3, 20000.00, 'DISPONIBLE'), (15, 4, 18000.00, 'DISPONIBLE'), (16, 2, 15000.00, 'DISPONIBLE'),
(17, 1, 12000.00, 'DISPONIBLE'), (18, 3, 20000.00, 'DISPONIBLE'), (19, 4, 18000.00, 'DISPONIBLE'), (20, 2, 15000.00, 'DISPONIBLE'),

(21, 2, 25000.00, 'DISPONIBLE'), (22, 2, 25000.00, 'DISPONIBLE'), (23, 3, 22000.00, 'DISPONIBLE'), (24, 2, 28000.00, 'DISPONIBLE'),
(25, 4, 30000.00, 'DISPONIBLE'), (26, 1, 19000.00, 'DISPONIBLE'), (27, 3, 22000.00, 'DISPONIBLE'), (28, 2, 25000.00, 'DISPONIBLE'),
(29, 4, 30000.00, 'DISPONIBLE'), (30, 2, 25000.00, 'DISPONIBLE'), (31, 3, 22000.00, 'DISPONIBLE'), (32, 1, 19000.00, 'DISPONIBLE'),
(33, 4, 30000.00, 'DISPONIBLE'), (34, 2, 25000.00, 'DISPONIBLE'), (35, 3, 22000.00, 'DISPONIBLE'), (36, 1, 19000.00, 'DISPONIBLE'),
(37, 2, 25000.00, 'DISPONIBLE'), (38, 3, 22000.00, 'DISPONIBLE'), (39, 4, 30000.00, 'DISPONIBLE'), (40, 2, 25000.00, 'DISPONIBLE'),

(41, 4, 20000.00, 'DISPONIBLE'), (42, 3, 16000.00, 'DISPONIBLE'), (43, 2, 14000.00, 'DISPONIBLE'), (44, 1, 10000.00, 'DISPONIBLE'),
(45, 4, 20000.00, 'DISPONIBLE'), (46, 3, 16000.00, 'DISPONIBLE'), (47, 2, 14000.00, 'DISPONIBLE'), (48, 1, 10000.00, 'DISPONIBLE'),
(49, 4, 20000.00, 'DISPONIBLE'), (50, 3, 16000.00, 'DISPONIBLE'), (51, 2, 14000.00, 'DISPONIBLE'), (52, 1, 10000.00, 'DISPONIBLE'),
(53, 4, 20000.00, 'DISPONIBLE'), (54, 3, 16000.00, 'DISPONIBLE'), (55, 2, 14000.00, 'DISPONIBLE'), (56, 1, 10000.00, 'DISPONIBLE'),
(57, 4, 20000.00, 'DISPONIBLE'), (58, 3, 16000.00, 'DISPONIBLE'), (59, 2, 14000.00, 'DISPONIBLE'), (60, 1, 10000.00, 'DISPONIBLE');