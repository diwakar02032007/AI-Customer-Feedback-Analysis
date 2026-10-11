-- ========================================================
-- AI-Powered Customer Feedback Analysis System
-- Database Schema for MySQL Community Edition
-- ========================================================

CREATE DATABASE IF NOT EXISTS `customer_feedback_db` 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `customer_feedback_db`;

-- Drop tables if re-initializing (in dependency order)
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `activity_logs`;
DROP TABLE IF EXISTS `reports`;
DROP TABLE IF EXISTS `feedback_aspects`;
DROP TABLE IF EXISTS `feedbacks`;
DROP TABLE IF EXISTS `categories`;
DROP TABLE IF EXISTS `users`;
SET FOREIGN_KEY_CHECKS = 1;

-- 1. Users Table (Admin & Customers)
CREATE TABLE `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(150) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `role` ENUM('admin', 'customer') NOT NULL DEFAULT 'customer',
    `phone` VARCHAR(20) DEFAULT NULL,
    `avatar` VARCHAR(255) DEFAULT 'default_avatar.png',
    `bio` TEXT DEFAULT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_users_email` (`email`),
    INDEX `idx_users_role` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Categories Table
CREATE TABLE `categories` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL UNIQUE,
    `description` VARCHAR(255) DEFAULT NULL,
    `is_active` BOOLEAN DEFAULT TRUE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Feedbacks Table
CREATE TABLE `feedbacks` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT DEFAULT NULL,
    `customer_name` VARCHAR(100) NOT NULL,
    `customer_email` VARCHAR(150) NOT NULL,
    `rating` INT NOT NULL CHECK (`rating` BETWEEN 1 AND 5),
    `feedback_text` TEXT NOT NULL,
    `category` VARCHAR(100) NOT NULL DEFAULT 'General',
    `status` ENUM('new', 'under_review', 'resolved', 'spam') NOT NULL DEFAULT 'new',
    `priority` ENUM('low', 'medium', 'high', 'critical') NOT NULL DEFAULT 'low',
    `sentiment` ENUM('positive', 'neutral', 'negative') NOT NULL DEFAULT 'neutral',
    `sentiment_score` DECIMAL(4, 2) NOT NULL DEFAULT 0.00,
    `emotion` VARCHAR(50) NOT NULL DEFAULT 'neutral',
    `aspect` VARCHAR(100) NOT NULL DEFAULT 'General',
    `aspect_sentiment` VARCHAR(50) NOT NULL DEFAULT 'neutral',
    `spam_probability` DECIMAL(4, 2) NOT NULL DEFAULT 0.00,
    `is_spam` BOOLEAN NOT NULL DEFAULT FALSE,
    `language` VARCHAR(50) NOT NULL DEFAULT 'English',
    `summary` TEXT DEFAULT NULL,
    `recommendation` TEXT DEFAULT NULL,
    `admin_notes` TEXT DEFAULT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_feedbacks_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    INDEX `idx_feedbacks_user` (`user_id`),
    INDEX `idx_feedbacks_sentiment` (`sentiment`),
    INDEX `idx_feedbacks_priority` (`priority`),
    INDEX `idx_feedbacks_status` (`status`),
    INDEX `idx_feedbacks_category` (`category`),
    INDEX `idx_feedbacks_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Feedback Aspects Table (Granular Aspect-Based Sentiment Analysis)
CREATE TABLE `feedback_aspects` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `feedback_id` INT NOT NULL,
    `aspect_name` VARCHAR(100) NOT NULL,
    `sentiment` VARCHAR(50) NOT NULL DEFAULT 'neutral',
    `confidence` DECIMAL(4, 2) NOT NULL DEFAULT 0.00,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_aspects_feedback` FOREIGN KEY (`feedback_id`) REFERENCES `feedbacks` (`id`) ON DELETE CASCADE,
    INDEX `idx_aspects_feedback` (`feedback_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Reports Table
CREATE TABLE `reports` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `report_title` VARCHAR(200) NOT NULL,
    `report_type` VARCHAR(50) NOT NULL DEFAULT 'summary',
    `date_from` DATE DEFAULT NULL,
    `date_to` DATE DEFAULT NULL,
    `total_feedbacks` INT NOT NULL DEFAULT 0,
    `positive_count` INT NOT NULL DEFAULT 0,
    `neutral_count` INT NOT NULL DEFAULT 0,
    `negative_count` INT NOT NULL DEFAULT 0,
    `avg_rating` DECIMAL(3, 2) NOT NULL DEFAULT 0.00,
    `file_path` VARCHAR(255) DEFAULT NULL,
    `created_by` INT DEFAULT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_reports_user` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Activity Logs Table
CREATE TABLE `activity_logs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT DEFAULT NULL,
    `action` VARCHAR(100) NOT NULL,
    `details` TEXT DEFAULT NULL,
    `ip_address` VARCHAR(50) DEFAULT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_logs_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
    INDEX `idx_logs_user` (`user_id`),
    INDEX `idx_logs_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
