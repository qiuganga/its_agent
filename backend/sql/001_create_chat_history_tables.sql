CREATE TABLE IF NOT EXISTS agent_chat_sessions (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id VARCHAR(128) NOT NULL,
    session_id VARCHAR(128) NOT NULL,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_agent_chat_sessions_user_session (user_id, session_id),
    KEY idx_agent_chat_sessions_user_updated (user_id, updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS agent_chat_messages (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    chat_session_id BIGINT UNSIGNED NOT NULL,
    message_order INT UNSIGNED NOT NULL,
    role VARCHAR(16) NOT NULL,
    content LONGTEXT NOT NULL,
    created_at DATETIME(6) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_agent_chat_messages_session_order (chat_session_id, message_order),
    KEY idx_agent_chat_messages_session_order (chat_session_id, message_order),
    CONSTRAINT fk_agent_chat_messages_session
        FOREIGN KEY (chat_session_id)
        REFERENCES agent_chat_sessions (id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
