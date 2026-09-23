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
-- Dumping routines for database 'icmt_faculty_directory'
--
/*!50003 DROP PROCEDURE IF EXISTS `sp_approve_membership_application` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_approve_membership_application`(
    IN p_application_id BIGINT,
    IN p_admin_id BIGINT
)
BEGIN

    DECLARE v_member_id VARCHAR(20);
    DECLARE v_new_member_id VARCHAR(20);

    DECLARE v_membership_category VARCHAR(100);
    DECLARE v_academic_title VARCHAR(30);
    DECLARE v_full_name VARCHAR(200);
    DECLARE v_date_of_birth DATE;
    DECLARE v_personal_email VARCHAR(255);
    DECLARE v_professional_email VARCHAR(255);
    DECLARE v_mobile VARCHAR(40);
    DECLARE v_whatsapp VARCHAR(40);
    DECLARE v_whatsapp_secondary VARCHAR(40);
    DECLARE v_photo_url TEXT;
    DECLARE v_highest_qualification TEXT;
    DECLARE v_designation VARCHAR(150);
    DECLARE v_department VARCHAR(200);
    DECLARE v_institution TEXT;
    DECLARE v_college_address TEXT;
    DECLARE v_pin_code VARCHAR(20);
    DECLARE v_state_province VARCHAR(100);
    DECLARE v_country VARCHAR(100);
    DECLARE v_google_scholar TEXT;
    DECLARE v_linkedin TEXT;
    DECLARE v_orcid VARCHAR(255);
    DECLARE v_expertise TEXT;
    DECLARE v_research_guideship TEXT;

    DECLARE v_approval_status VARCHAR(50);
    DECLARE v_existing_count INT DEFAULT 0;

    DECLARE v_next_number INT DEFAULT 0;
    DECLARE v_lock_acquired BOOLEAN DEFAULT FALSE;
    DECLARE v_created_new_member BOOLEAN DEFAULT FALSE;


    /* -----------------------------------------
       Error handler
       ----------------------------------------- */

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN

        IF v_lock_acquired THEN
            DO RELEASE_LOCK('icmt_member_id_generation');
        END IF;

        ROLLBACK;

        RESIGNAL;
    END;


    START TRANSACTION;


    /* -----------------------------------------
       1. Get application
       ----------------------------------------- */

    SELECT
        member_id,
        membership_category,
        academic_title,
        full_name,
        date_of_birth,
        personal_email,
        professional_email,
        mobile,
        whatsapp,
        whatsapp_secondary,
        photo_url,
        highest_qualification,
        designation,
        department,
        institution,
        college_address,
        pin_code,
        state_province,
        country,
        google_scholar,
        linkedin,
        orcid,
        expertise,
        research_guideship,
        approval_status
    INTO
        v_member_id,
        v_membership_category,
        v_academic_title,
        v_full_name,
        v_date_of_birth,
        v_personal_email,
        v_professional_email,
        v_mobile,
        v_whatsapp,
        v_whatsapp_secondary,
        v_photo_url,
        v_highest_qualification,
        v_designation,
        v_department,
        v_institution,
        v_college_address,
        v_pin_code,
        v_state_province,
        v_country,
        v_google_scholar,
        v_linkedin,
        v_orcid,
        v_expertise,
        v_research_guideship,
        v_approval_status
    FROM membership_applications
    WHERE application_id = p_application_id
    FOR UPDATE;


    /* -----------------------------------------
       2. Application must be Pending
       ----------------------------------------- */

    IF v_approval_status IS NULL THEN

        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Membership application not found';

    END IF;


    IF v_approval_status <> 'Pending' THEN

        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT =
        'Only Pending applications can be approved';

    END IF;


    /* -----------------------------------------
       3. Verify admin exists
       ----------------------------------------- */

    SELECT COUNT(*)
    INTO v_existing_count
    FROM admin_users
    WHERE admin_id = p_admin_id
      AND is_active = TRUE;


    IF v_existing_count = 0 THEN

        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT =
        'Invalid or inactive admin user';

    END IF;


    /* =================================================
       EXISTING MEMBER
       ================================================= */

    IF v_member_id IS NOT NULL
       AND TRIM(v_member_id) <> '' THEN


        /* Verify member exists */

        SELECT COUNT(*)
        INTO v_existing_count
        FROM members
        WHERE member_id = v_member_id;


        IF v_existing_count = 0 THEN

            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT =
            'Existing member ID was not found';

        END IF;


        /* -----------------------------------------
           Check email is not already used by another
           member
           ----------------------------------------- */

        IF v_professional_email IS NOT NULL
           AND TRIM(v_professional_email) <> '' THEN

            SELECT COUNT(*)
            INTO v_existing_count
            FROM members
            WHERE LOWER(TRIM(professional_email))
                    = LOWER(TRIM(v_professional_email))
              AND member_id <> v_member_id;


            IF v_existing_count > 0 THEN

                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT =
                'Professional email already belongs to another member';

            END IF;

        END IF;


        /* -----------------------------------------
           UPDATE EXISTING MEMBER
           ----------------------------------------- */

        UPDATE members
        SET
            academic_title = v_academic_title,
            name = v_full_name,
            date_of_birth = v_date_of_birth,
            qualification = v_highest_qualification,
            designation = v_designation,
            department = v_department,
            institution = v_institution,
            address = v_college_address,
            state_province = v_state_province,
            pin_code = v_pin_code,
            country = v_country,
            research_guideship = v_research_guideship,
            expertise = v_expertise,
            mobile = v_mobile,
            whatsapp = v_whatsapp,
            whatsapp_secondary = v_whatsapp_secondary,
            professional_email = v_professional_email,
            personal_email = v_personal_email,
            linkedin = v_linkedin,
            orcid = v_orcid,
            google_scholar = v_google_scholar,
            membership_category = v_membership_category,
            is_active = TRUE,
            my_status = 'Active',
            updated_at = NOW()
        WHERE member_id = v_member_id;


        SET v_created_new_member = FALSE;


    /* =================================================
       NEW MEMBER
       ================================================= */

    ELSE


        /* -----------------------------------------
           Acquire lock for member ID generation
           ----------------------------------------- */

        SELECT GET_LOCK(
            'icmt_member_id_generation',
            10
        )
        INTO v_lock_acquired;


        IF v_lock_acquired <> TRUE THEN

            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT =
            'Could not generate a unique member ID';

        END IF;


        /* -----------------------------------------
           Find next ICMT number
           ----------------------------------------- */

        SELECT
            COALESCE(
                MAX(
                    CAST(
                        SUBSTRING(member_id, 5)
                        AS UNSIGNED
                    )
                ),
                0
            )
        INTO v_next_number
        FROM members
        WHERE member_id REGEXP '^ICMT[0-9]+$';


        SET v_next_number = v_next_number + 1;


        SET v_new_member_id =
            CONCAT(
                'ICMT',
                LPAD(v_next_number, 3, '0')
            );


        /* -----------------------------------------
           Insert NEW member
           ----------------------------------------- */

        INSERT INTO members (
            member_id,
            academic_title,
            name,
            date_of_birth,
            qualification,
            designation,
            department,
            institution,
            address,
            pin_code,
            state_province,
            country,
            research_guideship,
            expertise,
            mobile,
            whatsapp,
            whatsapp_secondary,
            professional_email,
            personal_email,
            linkedin,
            orcid,
            google_scholar,
            photo_url,
            membership_category,
            is_active,
            source_record,
            my_status,
            created_at,
            updated_at
        )
        VALUES (
            v_new_member_id,
            v_academic_title,
            v_full_name,
            v_date_of_birth,
            v_highest_qualification,
            v_designation,
            v_department,
            v_institution,
            v_college_address,
            v_pin_code,
            v_state_province,
            v_country,
            v_research_guideship,
            v_expertise,
            v_mobile,
            v_whatsapp,
            v_whatsapp_secondary,
            v_professional_email,
            v_personal_email,
            v_linkedin,
            v_orcid,
            v_google_scholar,
            v_photo_url,
            v_membership_category,
            TRUE,
            CONCAT(
                'Membership Application #',
                p_application_id
            ),
            'Active',
            NOW(),
            NOW()
        );


        SET v_member_id = v_new_member_id;

        SET v_created_new_member = TRUE;


        DO RELEASE_LOCK(
            'icmt_member_id_generation'
        );

        SET v_lock_acquired = FALSE;

    END IF;


    /* -----------------------------------------
       4. Update application
       ----------------------------------------- */

    UPDATE membership_applications
    SET
        member_id = v_member_id,
        approval_status = 'Approved',
        reviewed_by = p_admin_id,
        reviewed_at = NOW(),
        updated_at = NOW()
    WHERE application_id = p_application_id;


    COMMIT;


    /* -----------------------------------------
       5. Return result
       ----------------------------------------- */

    SELECT
        p_application_id AS application_id,
        v_member_id AS member_id,
        v_created_new_member AS created_new_member,
        'Approved' AS approval_status;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_create_admin_user` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_create_admin_user`(
    IN p_user_id VARCHAR(100),
    IN p_password_hash VARCHAR(255),
    IN p_is_active BOOLEAN
)
BEGIN

    -- Validate user ID
    IF p_user_id IS NULL OR TRIM(p_user_id) = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid user_id';
    END IF;

    -- Validate password hash
    IF p_password_hash IS NULL OR TRIM(p_password_hash) = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Password hash is required';
    END IF;

    -- Check whether username already exists
    IF EXISTS (
        SELECT 1
        FROM admin_users
        WHERE user_id = TRIM(p_user_id)
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'User is already mapped to an admin';
    END IF;

    -- Create admin
    INSERT INTO admin_users (
        user_id,
        password_hash,
        is_active,
        created_at,
        updated_at
    )
    VALUES (
        TRIM(p_user_id),
        p_password_hash,
        COALESCE(p_is_active, TRUE),
        NOW(),
        NOW()
    );

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_create_membership_payment` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_create_membership_payment`(
    IN p_application_id BIGINT,
    IN p_member_id VARCHAR(20),
    IN p_membership_category VARCHAR(100),
    IN p_amount DECIMAL(10,2),
    IN p_currency CHAR(3),
    IN p_payment_method VARCHAR(50),
    IN p_payment_gateway VARCHAR(100),
    IN p_transaction_id VARCHAR(255),
    IN p_payment_status VARCHAR(50),
    IN p_paid_at DATETIME
)
BEGIN

    DECLARE v_application_member_id VARCHAR(20);
    DECLARE v_application_category VARCHAR(100);
    DECLARE v_application_status VARCHAR(50);
    DECLARE v_count INT DEFAULT 0;

    /* 1. Check application exists */

    SELECT COUNT(*)
    INTO v_count
    FROM membership_applications
    WHERE application_id = p_application_id;

    IF v_count = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Membership application does not exist';
    END IF;


    /* 2. Get application details */

    SELECT
        member_id,
        membership_category,
        approval_status
    INTO
        v_application_member_id,
        v_application_category,
        v_application_status
    FROM membership_applications
    WHERE application_id = p_application_id;


    /* 3. Validate member ID */

    IF p_member_id IS NOT NULL
       AND v_application_member_id IS NOT NULL
       AND p_member_id <> v_application_member_id THEN

        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT =
        'Member ID does not match the membership application';

    END IF;


    /* 4. Validate membership category */

    IF p_membership_category IS NULL
       OR TRIM(p_membership_category) = '' THEN

        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT =
        'Membership category is required';

    END IF;


    IF p_membership_category <> v_application_category THEN

        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT =
        'Membership category does not match the application';

    END IF;


    /* 5. Validate amount */

    IF p_amount IS NULL OR p_amount <= 0 THEN

        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT =
        'Payment amount must be greater than zero';

    END IF;


    /* 6. Validate currency */

    IF p_currency IS NULL
       OR UPPER(TRIM(p_currency)) <> 'INR' THEN

        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT =
        'Currency must be INR';

    END IF;


    /* 7. Validate payment status */

    IF p_payment_status IS NULL
       OR p_payment_status NOT IN
          ('Pending', 'Paid', 'Failed', 'Refunded') THEN

        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT =
        'Invalid payment status';

    END IF;


    /* 8. Transaction ID required for successful payment */

    IF p_payment_status = 'Paid'
       AND (
            p_transaction_id IS NULL
            OR TRIM(p_transaction_id) = ''
       ) THEN

        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT =
        'Transaction ID is required for paid payments';

    END IF;


    /* 9. Prevent duplicate transaction */

    IF p_transaction_id IS NOT NULL
       AND TRIM(p_transaction_id) <> ''
       AND EXISTS (
           SELECT 1
           FROM membership_payments
           WHERE transaction_id = p_transaction_id
       ) THEN

        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT =
        'Transaction ID already exists';

    END IF;


    /* 10. Insert payment */

    INSERT INTO membership_payments (
        application_id,
        member_id,
        membership_category,
        amount,
        currency,
        payment_method,
        payment_gateway,
        transaction_id,
        payment_status,
        paid_at,
        created_at,
        updated_at
    )
    VALUES (
        p_application_id,
        COALESCE(p_member_id, v_application_member_id),
        p_membership_category,
        p_amount,
        UPPER(p_currency),
        p_payment_method,
        p_payment_gateway,
        p_transaction_id,
        p_payment_status,
        p_paid_at,
        NOW(),
        NOW()
    );


    /* 11. Return payment ID */

    SELECT
        LAST_INSERT_ID() AS payment_id,
        p_application_id AS application_id,
        COALESCE(p_member_id, v_application_member_id) AS member_id,
        p_payment_status AS payment_status;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_submit_membership_application` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_submit_membership_application`(
    IN p_member_id VARCHAR(20),
    IN p_membership_category VARCHAR(100),
    IN p_academic_title VARCHAR(30),
    IN p_full_name VARCHAR(200),
    IN p_date_of_birth DATE,
    IN p_personal_email VARCHAR(255),
    IN p_professional_email VARCHAR(255),
    IN p_mobile VARCHAR(40),
    IN p_whatsapp VARCHAR(40),
    IN p_whatsapp_secondary VARCHAR(40),
    IN p_photo_url TEXT,
    IN p_highest_qualification TEXT,
    IN p_designation VARCHAR(150),
    IN p_department VARCHAR(200),
    IN p_institution TEXT,
    IN p_college_address TEXT,
    IN p_pin_code VARCHAR(20),
    IN p_state_province VARCHAR(100),
    IN p_country VARCHAR(100),
    IN p_google_scholar TEXT,
    IN p_linkedin TEXT,
    IN p_orcid VARCHAR(255),
    IN p_expertise TEXT,
    IN p_research_guideship TEXT
)
BEGIN

    DECLARE v_member_id VARCHAR(20) DEFAULT NULL;
    DECLARE v_application_id BIGINT;

    /* -----------------------------------------
       1. Basic validation
       ----------------------------------------- */

    IF p_full_name IS NULL OR TRIM(p_full_name) = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Full name is required';
    END IF;

    IF p_membership_category IS NULL
       OR TRIM(p_membership_category) = '' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Membership category is required';
    END IF;


    /* -----------------------------------------
       2. Check explicitly supplied member ID
       ----------------------------------------- */

    IF p_member_id IS NOT NULL
       AND TRIM(p_member_id) <> '' THEN

        SELECT member_id
        INTO v_member_id
        FROM members
        WHERE member_id = TRIM(p_member_id)
        LIMIT 1;

        IF v_member_id IS NULL THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Provided member ID does not exist';
        END IF;

    END IF;


    /* -----------------------------------------
       3. If member ID was not supplied,
          identify existing member by email/mobile
       ----------------------------------------- */

    IF v_member_id IS NULL THEN

        /* First check professional email */

        IF p_professional_email IS NOT NULL
           AND TRIM(p_professional_email) <> '' THEN

            SELECT member_id
            INTO v_member_id
            FROM members
            WHERE LOWER(TRIM(professional_email))
                  = LOWER(TRIM(p_professional_email))
            LIMIT 1;

        END IF;


        /* If not found, check mobile */

        IF v_member_id IS NULL
           AND p_mobile IS NOT NULL
           AND TRIM(p_mobile) <> '' THEN

            SELECT member_id
            INTO v_member_id
            FROM members
            WHERE TRIM(mobile) = TRIM(p_mobile)
            LIMIT 1;

        END IF;

    END IF;


    /* -----------------------------------------
       4. Prevent duplicate pending applications
       ----------------------------------------- */

    IF EXISTS (
        SELECT 1
        FROM membership_applications
        WHERE approval_status = 'Pending'
          AND (
                (
                    v_member_id IS NOT NULL
                    AND member_id = v_member_id
                )
                OR
                (
                    p_professional_email IS NOT NULL
                    AND TRIM(p_professional_email) <> ''
                    AND LOWER(TRIM(professional_email))
                        = LOWER(TRIM(p_professional_email))
                )
            )
    ) THEN

        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT =
        'A pending membership application already exists';

    END IF;


    /* -----------------------------------------
       5. Insert application
       ----------------------------------------- */

    INSERT INTO membership_applications (
        member_id,
        membership_category,
        academic_title,
        full_name,
        date_of_birth,
        personal_email,
        professional_email,
        mobile,
        whatsapp,
        whatsapp_secondary,
        photo_url,
        highest_qualification,
        designation,
        department,
        institution,
        college_address,
        pin_code,
        state_province,
        country,
        google_scholar,
        linkedin,
        orcid,
        expertise,
        research_guideship,
        approval_status,
        created_at,
        updated_at
    )
    VALUES (
        v_member_id,
        p_membership_category,
        p_academic_title,
        p_full_name,
        p_date_of_birth,
        p_personal_email,
        p_professional_email,
        p_mobile,
        p_whatsapp,
        p_whatsapp_secondary,
        p_photo_url,
        p_highest_qualification,
        p_designation,
        p_department,
        p_institution,
        p_college_address,
        p_pin_code,
        p_state_province,
        p_country,
        p_google_scholar,
        p_linkedin,
        p_orcid,
        p_expertise,
        p_research_guideship,
        'Pending',
        NOW(),
        NOW()
    );


    SET v_application_id = LAST_INSERT_ID();


    /* -----------------------------------------
       6. Return application information
       ----------------------------------------- */

    SELECT
        v_application_id AS application_id,
        v_member_id AS existing_member_id,
        'Pending' AS approval_status;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-23 23:06:14
