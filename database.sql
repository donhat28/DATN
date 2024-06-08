-- Database: user_management

-- DROP DATABASE IF EXISTS user_management;

-- CREATE DATABASE user_management
--     WITH
--     OWNER = postgres
--     ENCODING = 'UTF8'
--     LC_COLLATE = 'Vietnamese_Vietnam.1252'
--     LC_CTYPE = 'Vietnamese_Vietnam.1252'
--     LOCALE_PROVIDER = 'libc'
--     TABLESPACE = pg_default
--     CONNECTION LIMIT = -1
--     IS_TEMPLATE = False;

-- GRANT TEMPORARY, CONNECT ON DATABASE user_management TO PUBLIC;

-- GRANT ALL ON DATABASE user_management TO postgres;

-- GRANT CONNECT ON DATABASE user_management TO user_manager;

-- Bảng lưu thông tin người dùng
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
	name VARCHAR(50) NOT NULL UNIQUE,
    username VARCHAR(50) NOT NULL UNIQUE,  
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bảng lưu đặc điểm khuôn mặt
CREATE TABLE face_encodings (
    encoding_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    face_encoding BYTEA NOT NULL
);

-- Bảng lưu thông tin các lần đăng nhập
CREATE TABLE login_attempts (
    attempt_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN
);
