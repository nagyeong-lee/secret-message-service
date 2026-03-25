CREATE DATABASE secret_message_db;
USE secret_message_db;

CREATE TABLE secret_message (
    id INT AUTO_INCREMENT PRIMARY KEY,
    token VARCHAR(128) UNIQUE NOT NULL,
    encrypted_message LONGTEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);