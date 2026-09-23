-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: icmt_faculty_directory
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `membership_applications`
--

DROP TABLE IF EXISTS `membership_applications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `membership_applications` (
  `application_id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `member_id` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `membership_category` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `academic_title` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `full_name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `date_of_birth` date DEFAULT NULL,
  `personal_email` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `professional_email` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `mobile` varchar(40) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `whatsapp` varchar(40) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `whatsapp_secondary` varchar(40) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `photo_url` text COLLATE utf8mb4_unicode_ci,
  `highest_qualification` text COLLATE utf8mb4_unicode_ci,
  `designation` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `department` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `institution` text COLLATE utf8mb4_unicode_ci,
  `college_address` text COLLATE utf8mb4_unicode_ci,
  `pin_code` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `state_province` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `country` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `google_scholar` text COLLATE utf8mb4_unicode_ci,
  `linkedin` text COLLATE utf8mb4_unicode_ci,
  `orcid` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `expertise` text COLLATE utf8mb4_unicode_ci,
  `research_guideship` text COLLATE utf8mb4_unicode_ci,
  `approval_status` enum('Pending','Approved','Rejected') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Pending',
  `admin_notes` text COLLATE utf8mb4_unicode_ci,
  `reviewed_by` bigint unsigned DEFAULT NULL,
  `reviewed_at` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`application_id`),
  KEY `idx_application_member_id` (`member_id`),
  KEY `idx_application_status` (`approval_status`),
  KEY `idx_application_created_at` (`created_at`),
  KEY `fk_application_reviewed_by` (`reviewed_by`),
  CONSTRAINT `fk_application_reviewed_by` FOREIGN KEY (`reviewed_by`) REFERENCES `admin_users` (`admin_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `membership_applications`
--

LOCK TABLES `membership_applications` WRITE;
/*!40000 ALTER TABLE `membership_applications` DISABLE KEYS */;
INSERT INTO `membership_applications` VALUES (5,'ICMT381','Annual Membership Faculty','Dr.','PAYMENT TEST MEMBER','1995-05-10','payment.personal@example.com','payment.test@example.com','+91 9000000011','+91 9000000011',NULL,NULL,'Ph.D','Assistant Professor','Department of Commerce','Payment Test University','Nellore, Andhra Pradesh','524001','Andhra Pradesh','India',NULL,NULL,NULL,'Finance and Management','Payment Test University','Approved',NULL,8,'2026-09-22 16:54:04','2026-09-22 16:49:56','2026-09-22 16:54:04');
/*!40000 ALTER TABLE `membership_applications` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-23 23:06:14
