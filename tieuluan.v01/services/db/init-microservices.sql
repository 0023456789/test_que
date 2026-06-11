CREATE USER patient_user WITH PASSWORD 'patient_pass';
CREATE USER doctor_user WITH PASSWORD 'doctor_pass';
CREATE USER appointment_user WITH PASSWORD 'appointment_pass';
CREATE USER emr_user WITH PASSWORD 'emr_pass';
CREATE USER pharmacy_user WITH PASSWORD 'pharmacy_pass';
CREATE USER billing_user WITH PASSWORD 'billing_pass';
CREATE USER notification_user WITH PASSWORD 'notification_pass';

CREATE DATABASE patient_db OWNER patient_user;
CREATE DATABASE doctor_db OWNER doctor_user;
CREATE DATABASE appointment_db OWNER appointment_user;
CREATE DATABASE emr_db OWNER emr_user;
CREATE DATABASE pharmacy_db OWNER pharmacy_user;
CREATE DATABASE billing_db OWNER billing_user;
CREATE DATABASE notification_db OWNER notification_user;

GRANT ALL PRIVILEGES ON DATABASE patient_db TO patient_user;
GRANT ALL PRIVILEGES ON DATABASE doctor_db TO doctor_user;
GRANT ALL PRIVILEGES ON DATABASE appointment_db TO appointment_user;
GRANT ALL PRIVILEGES ON DATABASE emr_db TO emr_user;
GRANT ALL PRIVILEGES ON DATABASE pharmacy_db TO pharmacy_user;
GRANT ALL PRIVILEGES ON DATABASE billing_db TO billing_user;
GRANT ALL PRIVILEGES ON DATABASE notification_db TO notification_user;