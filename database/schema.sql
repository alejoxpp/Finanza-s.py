CREATE DATABASE IF NOT EXISTS finanzas_personales CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE finanzas_personales;

CREATE TABLE usuarios (
    id_usuario INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(150) NOT NULL UNIQUE,
    contrasena_hash VARCHAR(255) NOT NULL,
    fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categorias (
    id_categoria INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    tipo ENUM('ingreso', 'gasto') NOT NULL,
    CONSTRAINT fk_categorias_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT uq_categoria_usuario UNIQUE (id_usuario, nombre, tipo)
);

CREATE TABLE ingresos_gastos (
    id_movimiento INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    id_categoria INT NOT NULL,
    tipo ENUM('ingreso', 'gasto') NOT NULL,
    monto DECIMAL(10,2) NOT NULL CHECK (monto > 0),
    fecha DATE NOT NULL,
    descripcion VARCHAR(255) NULL,
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_movimiento_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_movimiento_categoria
        FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX idx_usuarios_correo ON usuarios(correo);
CREATE INDEX idx_categorias_usuario_tipo ON categorias(id_usuario, tipo);
CREATE INDEX idx_movimientos_usuario_fecha ON ingresos_gastos(id_usuario, fecha);
CREATE INDEX idx_movimientos_categoria ON ingresos_gastos(id_categoria);
CREATE INDEX idx_movimientos_tipo_fecha ON ingresos_gastos(tipo, fecha);
