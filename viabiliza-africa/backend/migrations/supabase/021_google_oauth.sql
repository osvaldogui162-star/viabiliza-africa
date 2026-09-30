-- ViabilizA+ África — Google OAuth (Continuar com Google)

ALTER TABLE public.users
    ALTER COLUMN password_hash DROP NOT NULL;

ALTER TABLE public.users
    ADD COLUMN IF NOT EXISTS google_id VARCHAR(255),
    ADD COLUMN IF NOT EXISTS auth_provider VARCHAR(20) NOT NULL DEFAULT 'email'
        CHECK (auth_provider IN ('email', 'google'));

CREATE UNIQUE INDEX IF NOT EXISTS idx_users_google_id
    ON public.users (google_id)
    WHERE google_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_users_auth_provider ON public.users (auth_provider);
