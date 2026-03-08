CREATE TABLE patent_basic (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,          -- 自增主键
    patent_internal_id VARCHAR(255) UNIQUE,        -- 接口中的唯一标识，如 'ZL_CN202511610595.7_CN121241842A_20260102'
    application_number VARCHAR(50) UNIQUE NOT NULL, -- 申请号，如 'CN202511610595.7' (对应JSON中的 "3")
    publication_number VARCHAR(50),                 -- 公开/公告号，如 'CN121241842A' (对应JSON中的 "4")
    title TEXT NOT NULL,                            -- 专利标题 (对应JSON中的 "2")
    patent_type VARCHAR(20),                        -- 专利类型，如 '发明专利' (对应JSON中的 "13")
    applicant TEXT,                                 -- 申请人/专利权人 (对应JSON中的 "7")
    application_date DATE,                          -- 申请日 (对应JSON中的 "15")
    publication_date DATE,                          -- 公开/公告日 (对应JSON中的 "16")
    country_code VARCHAR(10),                       -- 国别代码，如 'CN', 'US' (对应JSON中的 "17")
    language VARCHAR(10),                           -- 语言，如 'chi', 'eng' (对应JSON中的 "24")
    pdf_link VARCHAR(500),                          -- PDF链接 (对应JSON中的 "25")
    source_db VARCHAR(20) DEFAULT 'WF',            -- 数据来源，如 'WF' (万方)
    crawl_time DATETIME DEFAULT CURRENT_TIMESTAMP,  -- 爬取时间
    INDEX idx_application_number (application_number),
    INDEX idx_publication_number (publication_number),
    INDEX idx_application_date (application_date),
    INDEX idx_applicant (applicant(100)),          -- 前缀索引，因为可能较长
    INDEX idx_country (country_code)
);
CREATE TABLE inventor (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,                    -- 发明人姓名
    UNIQUE KEY uk_inventor_name (name)
);

CREATE TABLE patent_inventor_rel (
    patent_id BIGINT NOT NULL,                     -- 关联 patent_basic.id
    inventor_id INT NOT NULL,                      -- 关联 inventor.id
    display_order INT DEFAULT 0,                   -- 发明人顺序
    PRIMARY KEY (patent_id, inventor_id),
    FOREIGN KEY (patent_id) REFERENCES patent_basic(id) ON DELETE CASCADE,
    FOREIGN KEY (inventor_id) REFERENCES inventor(id) ON DELETE CASCADE
);
CREATE TABLE patent_full_text (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    patent_id BIGINT UNIQUE NOT NULL,              -- 关联 patent_basic.id
    abstract LONGTEXT,                             -- 专利摘要 (对应JSON中的 "12"，可能需要合并数组为字符串)
    claims LONGTEXT,                               -- 权利要求（如果后续有详细爬取）
    description LONGTEXT,                          -- 详细说明（如果后续有详细爬取）
    FOREIGN KEY (patent_id) REFERENCES patent_basic(id) ON DELETE CASCADE
);

-- 爬虫日志表
CREATE TABLE spider_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    spider_name VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    keyword VARCHAR(255),
    page INT,
    task_id VARCHAR(500),
    status VARCHAR(20) NOT NULL,
    error_msg TEXT,
    details TEXT,
    task_ids TEXT,
    patent_id VARCHAR(100),
    log_time DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
-- 另请注意：生产者任务存在于 Redis 列表 `wanfang:producer_tasks`，
-- 管理页面应当向其中推送包含 keyword 和 page_size 的 JSON 字符串。