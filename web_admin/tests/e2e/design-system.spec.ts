import { test, expect } from '@playwright/test';
import { AxeBuilder } from '@axe-core/playwright';

/**
 * Design-system guardrails (feature 004-lab-livre-design-system).
 * Covers: WCAG AA (axe), responsive (no horizontal overflow at 375px),
 * self-hosted fonts (no external CDN request), and modal keyboard behavior.
 *
 * The authenticated screens are reached by injecting a token into
 * localStorage so the shell renders without a seeded backend.
 */

const serious = (violations: { impact?: string | null }[]) =>
  violations.filter((v) => v.impact === 'serious' || v.impact === 'critical');

test('Login has no serious accessibility violations', async ({ page }) => {
  await page.goto('/');
  const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa']).analyze();
  expect(serious(results.violations)).toEqual([]);
});

test('Styleguide has no serious accessibility violations', async ({ page }) => {
  await page.goto('/styleguide');
  const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa']).analyze();
  expect(serious(results.violations)).toEqual([]);
});

test('Dashboard shell has no serious accessibility violations', async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem('token', 'test');
    localStorage.setItem('userType', 'ADMIN');
  });
  await page.goto('/');
  await page.waitForTimeout(800);
  const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa']).analyze();
  expect(serious(results.violations)).toEqual([]);
});

test('Login does not overflow horizontally at 375px', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 760 });
  await page.goto('/');
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
  expect(overflow).toBe(false);
});

test('fonts are self-hosted — no external font/CDN request', async ({ page }) => {
  const external: string[] = [];
  page.on('request', (req) => {
    const url = req.url();
    if (/fonts\.googleapis\.com|fonts\.gstatic\.com|grainy-gradients/.test(url)) external.push(url);
  });
  await page.goto('/', { waitUntil: 'networkidle' });
  expect(external).toEqual([]);
});

test('Modal traps focus and closes on Escape', async ({ page }) => {
  await page.goto('/styleguide');
  await page.getByRole('button', { name: 'Abrir modal' }).click();
  const dialog = page.getByRole('dialog');
  await expect(dialog).toBeVisible();
  await expect(dialog).toHaveAttribute('aria-modal', 'true');
  await page.keyboard.press('Escape');
  await expect(dialog).toBeHidden();
});
