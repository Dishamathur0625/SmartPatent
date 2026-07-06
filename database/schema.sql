-- SmartPatent Production SQL Schema

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    reset_token VARCHAR(255) DEFAULT NULL,
    reset_token_expiry DATETIME DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS drafts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) DEFAULT NULL,
    field TEXT DEFAULT NULL,
    draft_text LONGTEXT DEFAULT NULL,
    prior_art_analysis LONGTEXT DEFAULT NULL,
    diagram_path VARCHAR(512) DEFAULT NULL,
    diagram_caption TEXT DEFAULT NULL,
    drawing_description LONGTEXT DEFAULT NULL,
    version_no INT DEFAULT 1,
    is_edited BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_drafts_users FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
    INDEX idx_drafts_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS related_patents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    draft_id INT NOT NULL,
    patent_title TEXT DEFAULT NULL,
    patent_number VARCHAR(100) DEFAULT NULL,
    patent_url VARCHAR(512) DEFAULT NULL,
    abstract_text LONGTEXT DEFAULT NULL,
    similarity_percent FLOAT DEFAULT 0.0,
    CONSTRAINT fk_related_patents_drafts FOREIGN KEY (draft_id) REFERENCES drafts (id) ON DELETE CASCADE,
    INDEX idx_related_patents_draft_id (draft_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS draft_versions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    draft_id INT NOT NULL,
    version_no INT NOT NULL,
    draft_text LONGTEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_draft_versions_drafts FOREIGN KEY (draft_id) REFERENCES drafts (id) ON DELETE CASCADE,
    UNIQUE KEY uq_draft_id_version_no (draft_id, version_no),
    INDEX idx_draft_versions_draft_id (draft_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
