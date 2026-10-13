import { test, expect } from '@playwright/test';

/**
 * E2E (T018): an admin records a medical certificate and sees the justified-day count.
 *
 * Prerequisites (this spec talks to a live stack, so it is NOT run in unit CI):
 *   - Frontend running at BASE_URL (default http://localhost:5173)
 *   - Backend running and reachable from the frontend
 *   - An admin account (ADMIN_EMAIL / ADMIN_PASSWORD) and at least one ALUNO user
 * Run with:  ADMIN_EMAIL=... ADMIN_PASSWORD=... npx playwright test
 */

const ADMIN_EMAIL = process.env.ADMIN_EMAIL || 'admin@lablivre.unb.br';
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'changeme';

test('admin records a certificate and sees justified-day count', async ({ page }) => {
  // Login
  await page.goto('/');
  await page.getByPlaceholder(/e-?mail/i).fill(ADMIN_EMAIL);
  await page.getByPlaceholder(/senha/i).fill(ADMIN_PASSWORD);
  await page.getByRole('button', { name: /entrar|login/i }).click();

  // Open the Atestados panel
  await page.getByRole('button', { name: /atestados/i }).click();
  const dialog = page.getByRole('dialog', { name: /atestados médicos/i });
  await expect(dialog).toBeVisible();

  // Pick the first aluno, fill the period, attach a document
  await dialog.locator('#aluno-select').selectOption({ index: 0 });
  await dialog.locator('#cert-inicio').fill('2026-10-05');
  await dialog.locator('#cert-fim').fill('2026-10-09');
  await dialog.locator('#cert-file').setInputFiles({
    name: 'atestado.pdf',
    mimeType: 'application/pdf',
    buffer: Buffer.from('%PDF-1.4 e2e test'),
  });
  await dialog.getByRole('button', { name: /registrar atestado/i }).click();

  // A new certificate row appears with a justified-day count
  await expect(dialog.getByText(/dia\(s\) justificado\(s\)/i).first()).toBeVisible();
});
