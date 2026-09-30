-- UC17 — QR Code na fatura proforma

ALTER TABLE public.proforma_invoices
    ADD COLUMN IF NOT EXISTS qr_code_data TEXT,
    ADD COLUMN IF NOT EXISTS qr_code_image TEXT;

COMMENT ON COLUMN public.proforma_invoices.qr_code_data IS 'URL de verificação codificada no QR';
COMMENT ON COLUMN public.proforma_invoices.qr_code_image IS 'Imagem PNG do QR em base64';
