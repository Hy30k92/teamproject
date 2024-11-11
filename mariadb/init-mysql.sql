CREATE DATABASE IF NOT EXISTS ubuntu;
CREATE USER IF NOT EXISTS 'ubuntu'@'%' IDENTIFIED BY 'ubuntu';
GRANT ALL PRIVILEGES ON ubuntu.* TO 'ubuntu'@'%';
FLUSH PRIVILEGES;