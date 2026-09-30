-- Registo público com OTP por email + reforço de billing

ALTER TABLE public.users
    ADD COLUMN IF NOT EXISTS email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMPTZ;

-- Utilizadores existentes considerados verificados
UPDATE public.users
SET email_verified = TRUE,
    email_verified_at = COALESCE(email_verified_at, created_at)
WHERE email_verified = FALSE;

CREATE TABLE IF NOT EXISTS public.email_otp_codes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) NOT NULL,
    purpose         VARCHAR(20)  NOT NULL DEFAULT 'signup'
                    CHECK (purpose IN ('signup')),
    code_hash       VARCHAR(64)  NOT NULL,
    full_name       VARCHAR(200) NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    attempts        INT          NOT NULL DEFAULT 0,
    expires_at      TIMESTAMPTZ  NOT NULL,
    consumed_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_email_otp_email ON public.email_otp_codes (email);
CREATE INDEX IF NOT EXISTS idx_email_otp_expires ON public.email_otp_codes (expires_at);

ALTER TABLE public.subscription_payments
    ADD COLUMN IF NOT EXISTS subscription_id UUID
    REFERENCES public.user_subscriptions(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_subscription_payments_subscription
    ON public.subscription_payments (subscription_id);

ALTER TABLE public.email_otp_codes ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "service_role_email_otp" ON public.email_otp_codes;
CREATE POLICY "service_role_email_otp" ON public.email_otp_codes
    FOR ALL USING (true) WITH CHECK (true);
