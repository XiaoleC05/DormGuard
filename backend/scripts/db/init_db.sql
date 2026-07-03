-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS dorm_power_guard CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE dorm_power_guard;

-- 注意：表结构会由SQLAlchemy自动创建，此文件仅供参考
-- 如果需要手动创建，可以使用以下SQL

-- 电费记录表
-- 存储从西华大学电费系统抓取的电费数据，包括余量和用电量信息。
-- 支持多宿舍监控，每个宿舍通过dorm_number和room_id关联。
CREATE TABLE IF NOT EXISTS power_records (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID，自增',
    dorm_number VARCHAR(50) NOT NULL COMMENT '宿舍号（如：320、324），用于标识不同的宿舍',
    balance FLOAT NOT NULL COMMENT '电费余量（度），主要监控项，通常是空调余量，用于判断是否需要告警',
    kbalance FLOAT NULL COMMENT '空调余量（度），从API获取的空调专用电费余量',
    zbalance FLOAT NULL COMMENT '照明余量（度），从API获取的照明专用电费余量',
    kpower_consumption FLOAT NULL COMMENT '空调用电量（度），与上次记录的差值，表示本次记录周期内的空调用电量',
    zpower_consumption FLOAT NULL COMMENT '照明用电量（度），与上次记录的差值，表示本次记录周期内的照明用电量',
    power_consumption FLOAT NULL COMMENT '用电量（度），已废弃，保留用于兼容性，请使用kpower_consumption和zpower_consumption',
    record_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录时间，数据抓取的时间点',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间，记录插入数据库的时间',
    INDEX idx_dorm_number (dorm_number),
    INDEX idx_record_time (record_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='电费记录表';

-- 告警规则表
CREATE TABLE IF NOT EXISTS alert_rules (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID，自增',
    dorm_number VARCHAR(50) NOT NULL COMMENT '宿舍号（如：320、324），唯一标识一个宿舍的告警规则',
    room_id VARCHAR(50) NULL COMMENT '房间ID（roomid），从西华大学电费系统API获取，用于查询该宿舍的电费数据',
    kthreshold FLOAT NULL COMMENT '空调告警阈值（度），当空调余量低于此值时触发告警',
    zthreshold FLOAT NULL COMMENT '照明告警阈值（度），当照明余量低于此值时触发告警',
    enabled BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否启用告警规则，False时不会触发任何告警',
    qq_enabled BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否启用QQ告警',
    last_alert_time DATETIME NULL COMMENT '最后告警时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_dorm_number (dorm_number),
    INDEX idx_enabled (enabled)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='告警规则表';

-- 告警日志表
-- 记录所有告警发送的历史记录，包括成功和失败的告警，用于审计和问题排查。
CREATE TABLE IF NOT EXISTS alert_logs (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID，自增',
    dorm_number VARCHAR(50) NOT NULL COMMENT '宿舍号（如：320、324），标识触发告警的宿舍',
    alert_category VARCHAR(20) NULL COMMENT '告警类别：ac（空调）/light（照明），标识是哪个类型的电费余量触发了告警',
    balance FLOAT NOT NULL COMMENT '触发告警时的余量（度），记录告警触发时的实际电费余量',
    threshold FLOAT NOT NULL COMMENT '告警阈值（度），记录触发告警时使用的阈值',
    alert_type VARCHAR(20) NOT NULL COMMENT '告警类型：qq（QQ告警）',
    alert_status VARCHAR(20) NOT NULL COMMENT '告警状态：success（发送成功）/failed（发送失败），标识告警是否成功发送',
    alert_message TEXT NULL COMMENT '告警消息内容，记录实际发送的告警消息文本',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间，告警发送的时间',
    INDEX idx_dorm_number (dorm_number),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='告警日志表';
