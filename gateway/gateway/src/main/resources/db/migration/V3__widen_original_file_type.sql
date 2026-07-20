-- MIME types like application/vnd.openxmlformats-officedocument.wordprocessingml.document
-- exceed VARCHAR(50) and break task creation.
ALTER TABLE tasks
    ALTER COLUMN original_file_type TYPE VARCHAR(255);
