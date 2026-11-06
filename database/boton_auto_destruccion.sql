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