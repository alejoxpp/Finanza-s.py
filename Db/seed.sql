USE finanzas_personales;

INSERT INTO usuarios (nombre, correo, contrasena_hash)
VALUES ('Ana Torres', 'ana@example.com', '$2b$12$eImiTXuWVxfM37uY4JANjOL.81F8Rz.H5G3.xZ32s.zYx8Z32s.zY'); -- Password hashed

INSERT INTO categorias (nombre, tipo, id_usuario) VALUES
('Salario', 'ingreso', 1),
('Freelance', 'ingreso', 1),
('Alimentación', 'gasto', 1),
('Transporte', 'gasto', 1),
('Entretenimiento', 'gasto', 1),
('Salud', 'gasto', 1);

INSERT INTO ingresos_gastos (id_usuario, id_categoria, tipo, monto, fecha, descripcion) VALUES
(1, 1, 'ingreso', 2500000.00, '2026-06-01', 'Pago mensual'),
(1, 3, 'gasto', 320000.00, '2026-06-05', 'Mercado del mes'),
(1, 4, 'gasto', 90000.00,  '2026-06-07', 'Transporte semanal'),
(1, 5, 'gasto', 150000.00, '2026-06-10', 'Cine y salidas'),
(1, 1, 'ingreso', 2500000.00, '2026-07-01', 'Pago mensual'),
(1, 3, 'gasto', 300000.00, '2026-07-04', 'Mercado del mes'),
(1, 6, 'gasto', 800000.00, '2026-07-15', 'Consulta médica de urgencia');