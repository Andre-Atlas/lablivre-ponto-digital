import { test, expect } from '@playwright/test';

/**
 * E2E (T020): a mentor evaluates a student for a week and the save persists.
 *
 * Prerequisites (talks to a live stack, NOT run in unit CI):
 *   - Frontend at BASE_URL (default http://localhost:5173), backend reachable
 *   - A seeded LO catalog and program config (lo_eval_data_inicio / lo_eval_num_semanas)
 *   - A mentor (STAFF/ADMIN) account and at least one ALUNO in the mentor's turma
 * Run: MENTOR_EMAIL=... MENTOR_PASSWORD=... npx playwright test
 */

const EMAIL = process.env.MENTOR_EMAIL || 'mentor@lablivre.unb.br';
const PASSWORD = process.env.MENTOR_PASSWORD || 'changeme';

test('mentor records a weekly LO evaluation', async ({ page }) => {
  await page.goto('/');
  await page.getByPlaceholder(/e-?mail/i).fill(EMAIL);
  await page.getByPlaceholder(/senha/i).fill(PASSWORD);
  await page.getByRole('button', { name: /entrar|login/i }).click();

  await page.getByRole('button', { name: /avaliar/i }).click();
  const dialog = page.getByRole('dialog', { name: /avaliação de los/i });
  await expect(dialog).toBeVisible();

  // Pick the first student and set a level on the first LO, then save
  await dialog.locator('#av-aluno').selectOption({ index: 0 });
  const firstLevel = dialog.getByLabel(/nível de/i).first();
  await firstLevel.selectOption('3');
  await dialog.locator('#av-coment').fill('Avaliação E2E');
  await dialog.getByRole('button', { name: /salvar avaliação/i }).click();

  await expect(dialog.getByText(/avaliação salva/i)).toBeVisible();
});
