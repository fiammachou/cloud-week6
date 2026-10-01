CREATE TABLE IF NOT EXISTS visits (
    id INT PRIMARY KEY,
    count INT NOT NULL
);

INSERT INTO visits (id, count)
VALUES (1, 0)
ON DUPLICATE KEY UPDATE count = count;