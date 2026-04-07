-- MakerGit database migration script
-- Run this on an existing database to add new columns gracefully

-- Add password_hash column to users table if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'users' AND column_name = 'password_hash') THEN
        ALTER TABLE users ADD COLUMN password_hash text NOT NULL DEFAULT '';
        RAISE NOTICE 'Added password_hash column to users table';
    ELSE
        RAISE NOTICE 'password_hash column already exists in users table';
    END IF;
END $$;

-- Add api_key column to users table if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'users' AND column_name = 'api_key') THEN
        ALTER TABLE users ADD COLUMN api_key text UNIQUE;
        RAISE NOTICE 'Added api_key column to users table';
    ELSE
        RAISE NOTICE 'api_key column already exists in users table';
    END IF;
END $$;

-- Create index on api_key if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_users_api_key') THEN
        CREATE INDEX idx_users_api_key ON users(api_key);
        RAISE NOTICE 'Created index idx_users_api_key on users table';
    ELSE
        RAISE NOTICE 'Index idx_users_api_key already exists';
    END IF;
END $$;

-- Note: For existing users, you'll need to set password_hash and api_key manually
-- or run a script to generate them. This migration only adds the columns.