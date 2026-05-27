CREATE DATABASE IF NOT EXISTS siu2_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE siu2_db;


CREATE TABLE IF NOT EXISTS materias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    codigo VARCHAR(50) NULL UNIQUE
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS tipos_evaluacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    es_grupal BOOLEAN NOT NULL DEFAULT FALSE
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    dni BIGINT NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    es_admin BOOLEAN NOT NULL DEFAULT FALSE,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS estudiantes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL UNIQUE,
    padron BIGINT NOT NULL UNIQUE,
    carrera VARCHAR(150) NOT NULL,
    anio_ingreso INT NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_estudiantes_usuarios
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS profesores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL UNIQUE,
    legajo BIGINT NOT NULL UNIQUE,
    titulo VARCHAR(150) NOT NULL,
    departamento VARCHAR(100) NOT NULL,
    fecha_ingreso DATE NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_profesores_usuarios
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        ON DELETE CASCADE ON UPDATE CASCADE
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
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_evaluaciones_cursos 
        FOREIGN KEY (curso_id) REFERENCES cursos(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_evaluaciones_tipos_evaluacion 
        FOREIGN KEY (tipo_evaluacion_id) REFERENCES tipos_evaluacion(id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS equipos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    curso_id INT NOT NULL,
    evaluacion_id INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_equipos_cursos 
        FOREIGN KEY (curso_id) REFERENCES cursos(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_equipos_evaluaciones 
        FOREIGN KEY (evaluacion_id) REFERENCES evaluaciones(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS notas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    evaluacion_id INT NOT NULL,
    alumno_id INT NULL,
    equipo_id INT NULL,
    nota DECIMAL(4,2) NOT NULL,
    observaciones TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_notas_evaluaciones 
        FOREIGN KEY (evaluacion_id) REFERENCES evaluaciones(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_notas_usuarios 
        FOREIGN KEY (alumno_id) REFERENCES usuarios(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_notas_equipos 
        FOREIGN KEY (equipo_id) REFERENCES equipos(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT uq_evaluacion_alumno 
    UNIQUE (evaluacion_id, alumno_id),
    CONSTRAINT uq_evaluacion_equipo
        UNIQUE (evaluacion_id, equipo_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS equipo_integrantes (
    equipo_id INT NOT NULL,
    alumno_id INT NOT NULL,
    PRIMARY KEY (equipo_id, alumno_id), 
    CONSTRAINT fk_equipo_integrantes_equipos 
        FOREIGN KEY (equipo_id) REFERENCES equipos(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_equipo_integrantes_estudiantes
        FOREIGN KEY (alumno_id) REFERENCES estudiantes(id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS clases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL,
    profesor_id INT NOT NULL, 
    curso_id INT NOT NULL,
    fecha_hora_inicio DATETIME NOT NULL,
    fecha_hora_fin DATETIME NOT NULL,
    tema VARCHAR(255) NULL,
    status ENUM('pendiente', 'suspendida', 'en curso', 'finalizada') NOT NULL DEFAULT 'pendiente', -- CUALQUIER CAMBIO EN LOS ESTADOS, SE DEBE CAMBIAR EN CONFIG.PY 
    deleted_at TIMESTAMP NULL DEFAULT NULL, -- soft delete. mucho mejor que activo: boolean
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_clases_cursos
        FOREIGN KEY (curso_id) REFERENCES cursos(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_clases_profesores
        FOREIGN KEY (profesor_id) REFERENCES profesores(id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;
ALTER TABLE clases ADD INDEX idx_clases_busqueda (deleted_at, fecha_hora_inicio); -- hace las busquedas mas rapidas

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
    CONSTRAINT fk_asistencias_estudiantes
        FOREIGN KEY (alumno_id) REFERENCES estudiantes(id)
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