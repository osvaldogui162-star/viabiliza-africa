-- Utilizadores self-service (com assinatura activa) devem poder criar projectos.
-- Contas criadas via signup OTP antes da correcção ficaram com role=user.

UPDATE public.users u
SET role = 'financial', updated_at = NOW()
WHERE u.role = 'user'
  AND EXISTS (
    SELECT 1
    FROM public.user_subscriptions us
    WHERE us.user_id = u.id
      AND us.status = 'active'
  );
