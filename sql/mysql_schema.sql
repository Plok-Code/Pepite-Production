-- Wildflix - schema MySQL (utf8mb4)
-- 1) Creez une base : CREATE DATABASE wildflix CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- 2) Puis exécutez ce script dans cette base.

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  pseudo VARCHAR(64) NOT NULL,
  role VARCHAR(16) NOT NULL DEFAULT 'user',
  salt VARCHAR(64) NOT NULL,
  password_hash VARCHAR(128) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS favorites (
  user_id INT NOT NULL,
  imdb_key VARCHAR(32) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id, imdb_key),
  CONSTRAINT fk_fav_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

