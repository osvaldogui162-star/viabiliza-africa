-- Preferência de moeda do utilizador (AOA | USD | EUR)
ALTER TABLE public.users
    ADD COLUMN IF NOT EXISTS preferred_currency VARCHAR(5) NOT NULL DEFAULT 'AOA'
    CHECK (preferred_currency IN ('AOA', 'USD', 'EUR'));

UPDATE public.users
SET preferred_currency = 'AOA'
WHERE preferred_currency IS NULL OR preferred_currency NOT IN ('AOA', 'USD', 'EUR');
