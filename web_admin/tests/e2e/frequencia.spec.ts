import { test, expect } from '@playwright/test';
import { AxeBuilder } from '@axe-core/playwright';

/**
 * E2E da US1 (frequência lançada pelo mentor). Requer a stack ativa com uma
 * turma cadastrada, alunos ATIVOS nessa turma e um mentor (STAFF/ADMIN).
 * Credenciais via env (MENTOR_EMAIL/MENTOR_SENHA) ou os defaults de demo.
 */
const EMAIL = process.env.MENTOR_EMAIL || 'admin@lablivre.dev';
const SENHA = process.env.MENTOR_SENHA || 'lablivre123';
const TURMA = process.env.E2E_TURMA || 'Turma 2';

async function login(page: import('@playwright/test').Page) {
  await page.goto('/login');
  await page.getByPlaceholder('nome@lablivre.com').fill(EMAIL);
  await page.getByPlaceholder('••••••••').fill(SENHA);
  await page.locator('button[type=submit]').click();
  await page.waitForTimeout(1000);
}

test('mentor lança frequência e marca falta', async ({ page }) => {
  await login(page);
  await page.getByRole('link', { name: 'Frequência' }).click();
  await page.locator('select').first().selectOption(TURMA);
  await page.waitForTimeout(800);

  const alunos = page.locator('ul li');
  expect(await alunos.count()).toBeGreaterThan(0);

  await page.getByRole('button', { name: /Presente/ }).nth(0).click();
  await page.getByRole('button', { name: /Falta/ }).nth(1).click();
  await page.getByRole('button', { name: 'Salvar frequência' }).click();
  await expect(page.getByText('Frequência salva.')).toBeVisible();
});

test('página de frequência sem violações sérias de acessibilidade', async ({ page }) => {
  await login(page);
  await page.getByRole('link', { name: 'Frequência' }).click();
  await page.waitForTimeout(600);
  const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa']).analyze();
  const serious = results.violations.filter((v) => v.impact === 'serious' || v.impact === 'critical');
  expect(serious).toEqual([]);
});

test('aba de Atestados não existe mais', async ({ page }) => {
  await login(page);
  await expect(page.getByRole('link', { name: 'Atestados' })).toHaveCount(0);
});
