CREATE DATABASE IF NOT EXISTS campuspro CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE campuspro;

CREATE TABLE IF NOT EXISTS user (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  email VARCHAR(160) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(20) NOT NULL DEFAULT 'student',
  department VARCHAR(100) DEFAULT 'Computer Science',
  is_active_account BOOLEAN NOT NULL DEFAULT TRUE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX ix_user_email (email)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS project (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(180) NOT NULL,
  abstract TEXT NOT NULL,
  tech_stack VARCHAR(300) DEFAULT '',
  project_url VARCHAR(500) DEFAULT '',
  attachment VARCHAR(255) DEFAULT '',
  status VARCHAR(30) NOT NULL DEFAULT 'Submitted',
  feedback TEXT,
  owner_id INT NOT NULL,
  faculty_id INT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_project_owner FOREIGN KEY (owner_id) REFERENCES user(id),
  CONSTRAINT fk_project_faculty FOREIGN KEY (faculty_id) REFERENCES user(id),
  INDEX ix_project_status (status),
  INDEX ix_project_owner (owner_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS notification (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  message VARCHAR(255) NOT NULL,
  is_read BOOLEAN NOT NULL DEFAULT FALSE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_notification_user FOREIGN KEY (user_id) REFERENCES user(id),
  INDEX ix_notification_user_read (user_id, is_read)
) ENGINE=InnoDB;
