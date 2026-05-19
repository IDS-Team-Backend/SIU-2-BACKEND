CREATE DATABASE IF NOT EXISTS siu2_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE siu2_db;


CREATE TABLE IF NOT EXISTS tipos_usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS materias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    codigo VARCHAR(50) NULL UNIQUE
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS tipos_evaluacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    dni BIGINT NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    tipo_usuario_id INT NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_usuarios_tipos_usuario 
        FOREIGN KEY (tipo_usuario_id) REFERENCES tipos_usuario(id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS cursos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    materia_id INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    anio INT NOT NULL,
    cuatrimestre INT NOT NULL,
    CONSTRAINT fk_cursos_materias 
        FOREIGN KEY (materia_id) REFERENCES materias(id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS curso_usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    curso_id INT NOT NULL,
    usuario_id INT NOT NULL,
    estado ENUM('activo', 'abandono') NOT NULL DEFAULT 'activo',
    fecha_inscripcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_curso_usuarios_cursos 
        FOREIGN KEY (curso_id) REFERENCES cursos(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_curso_usuarios_usuarios 
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT uq_curso_usuario 
        UNIQUE (curso_id, usuario_id) 
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS evaluaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    curso_id INT NOT NULL,
    tipo_evaluacion_id INT NOT NULL,
    titulo VARCHAR(150) NOT NULL,
    descripcion TEXT NULL,
    fecha DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_evaluaciones_cursos 
        FOREIGN KEY (curso_id) REFERENCES cursos(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_evaluaciones_tipos_evaluacion 
        FOREIGN KEY (tipo_evaluacion_id) REFERENCES tipos_evaluacion(id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS notas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    evaluacion_id INT NOT NULL,
    alumno_id INT NOT NULL,
    nota DECIMAL(4,2) NOT NULL,
    observaciones TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_notas_evaluaciones 
        FOREIGN KEY (evaluacion_id) REFERENCES evaluaciones(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_notas_usuarios 
        FOREIGN KEY (alumno_id) REFERENCES usuarios(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT uq_evaluacion_alumno 
        UNIQUE (evaluacion_id, alumno_id) 
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS equipos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    curso_id INT NOT NULL,
    evaluacion_id INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_equipos_cursos 
        FOREIGN KEY (curso_id) REFERENCES cursos(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_equipos_evaluaciones 
        FOREIGN KEY (evaluacion_id) REFERENCES evaluaciones(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS equipo_integrantes (
    equipo_id INT NOT NULL,
    alumno_id INT NOT NULL,
    PRIMARY KEY (equipo_id, alumno_id), 
    CONSTRAINT fk_equipo_integrantes_equipos 
        FOREIGN KEY (equipo_id) REFERENCES equipos(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_equipo_integrantes_usuarios 
        FOREIGN KEY (alumno_id) REFERENCES usuarios(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS clases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    curso_id INT NOT NULL,
    fecha DATE NOT NULL,
    tema VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_clases_cursos 
        FOREIGN KEY (curso_id) REFERENCES cursos(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- guarda temporalmente los tokens generados para la asistencia por QR
CREATE TABLE IF NOT EXISTS qr_asistencia (
    id INT AUTO_INCREMENT PRIMARY KEY,
    clase_id INT NOT NULL,
    token VARCHAR(255) NOT NULL UNIQUE,
    expiracion DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_qr_asistencia_clases 
        FOREIGN KEY (clase_id) REFERENCES clases(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS asistencias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    clase_id INT NOT NULL,
    alumno_id INT NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_asistencias_clases 
        FOREIGN KEY (clase_id) REFERENCES clases(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_asistencias_usuarios 
        FOREIGN KEY (alumno_id) REFERENCES usuarios(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT uq_clase_alumno 
        UNIQUE (clase_id, alumno_id) 
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS materiales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    curso_id INT NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    archivo_url VARCHAR(255) NOT NULL,
    subido_por INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_materiales_cursos 
        FOREIGN KEY (curso_id) REFERENCES cursos(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_materiales_usuarios 
        FOREIGN KEY (subido_por) REFERENCES usuarios(id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NULL,
    accion VARCHAR(50) NOT NULL,
    endpoint VARCHAR(255) NULL,
    metodo VARCHAR(10) NULL,
    detalle TEXT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_logs_usuarios 
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;