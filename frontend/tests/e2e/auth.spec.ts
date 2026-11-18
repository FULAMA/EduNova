import { test, expect } from '@playwright/test';

/**
 * Tests E2E pour les parcours d'authentification EduNova
 * 
 * Prérequis:
 * - Backend démarré sur http://127.0.0.1:8017
 * - Frontend démarré sur http://127.0.0.1:5173
 */

test.describe('EduNova Authentication E2E Tests', () => {
  test.beforeEach(async ({ page, context }) => {
    // Configurer le contexte pour ignorer les erreurs CORS
    context.setDefaultTimeout(10000);
    
    // Attendre que le frontend soit prêt
    await page.goto('http://127.0.0.1:5173', { waitUntil: 'domcontentloaded' });
    
    // Attendre que le chargement soit terminé
    await page.waitForLoadState('networkidle');
  });

  // Test 1: Page de login accessible
  test('01 - Login page should be accessible', async ({ page }) => {
    await expect(page).toHaveURL(/login/);
    await expect(page).toHaveTitle(/EduNova/);
    
    // Vérifier la présence des champs email et password
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
  });

  // Test 2: Navigation vers la page d'inscription
  test('02 - Should navigate to register page', async ({ page }) => {
    // Cliquer sur le lien d'inscription
    await page.click('a[href*="register"]');
    await expect(page).toHaveURL(/register/);
    
    // Vérifier les champs du formulaire d'inscription
    await expect(page.locator('input[name="school_name"]')).toBeVisible();
    await expect(page.locator('input[name="admin_name"]')).toBeVisible();
    await expect(page.locator('input[name="email"]')).toBeVisible();
    await expect(page.locator('input[name="password"]')).toBeVisible();
    await expect(page.locator('input[name="confirm_password"]')).toBeVisible();
  });

  // Test 3: Inscription d'un nouvel établissement
  test('03 - Should register a new establishment', async ({ page, context }) => {
    // Aller à la page d'inscription
    await page.goto('http://127.0.0.1:5173/register');
    await page.waitForLoadState('networkidle');
    
    // Générer un email unique pour éviter les conflits
    const timestamp = Date.now();
    const email = `test.e2e.${timestamp}@example.com`;
    
    // Remplir le formulaire
    await page.fill('input[name="school_name"]', 'Test E2E School');
    await page.fill('input[name="admin_name"]', 'Test E2E Admin');
    await page.fill('input[name="email"]', email);
    await page.fill('input[name="password"]', 'E2EPassword123!');
    await page.fill('input[name="confirm_password"]', 'E2EPassword123!');
    
    // Soumettre le formulaire
    await page.click('button[type="submit"]');
    
    // Attendre la redirection (3 secondes)
    await page.waitForTimeout(4000);
    
    // Vérifier la redirection vers la page de login
    await expect(page).toHaveURL(/login/);
    
    // Vérifier le message de succès (optionnel)
    // Note: Cela dépend de l'implémentation du frontend
  });

  // Test 4: Connexion avec un compte valide
  test('04 - Should login with valid credentials', async ({ page, context }) => {
    // Utiliser un compte créé précédemment ou créer-en un nouveau
    const timestamp = Date.now();
    const email = `test.login.${timestamp}@example.com`;
    
    // D'abord, s'inscrire
    await page.goto('http://127.0.0.1:5173/register');
    await page.waitForLoadState('networkidle');
    
    await page.fill('input[name="school_name"]', 'Login Test School');
    await page.fill('input[name="admin_name"]', 'Login Test Admin');
    await page.fill('input[name="email"]', email);
    await page.fill('input[name="password"]', 'LoginPassword123!');
    await page.fill('input[name="confirm_password"]', 'LoginPassword123!');
    
    await page.click('button[type="submit"]');
    await page.waitForTimeout(4000);
    
    // Maintenant, se connecter
    await page.goto('http://127.0.0.1:5173/login');
    await page.waitForLoadState('networkidle');
    
    await page.fill('input[type="email"]', email);
    await page.fill('input[type="password"]', 'LoginPassword123!');
    
    await page.click('button[type="submit"]');
    
    // Attendre la connexion (redirection ou chargement)
    await page.waitForTimeout(2000);
    
    // Vérifier que nous ne sommes plus sur la page de login
    // (ou que nous avons été redirigés)
    // Note: Cela dépend de l'implémentation du frontend
    const current_url = page.url();
    expect(current_url).not.toContain('/login');
  });

  // Test 5: Validation des champs du formulaire d'inscription
  test('05 - Register form validation', async ({ page }) => {
    await page.goto('http://127.0.0.1:5173/register');
    await page.waitForLoadState('networkidle');
    
    // Essayer de soumettre un formulaire vide
    await page.click('button[type="submit"]');
    
    // Vérifier que les erreurs de validation sont affichées
    // Note: Cela dépend de l'implémentation du frontend
    await page.waitForTimeout(1000);
    
    // Vérifier qu'on est toujours sur la page d'inscription
    await expect(page).toHaveURL(/register/);
  });

  // Test 6: Gestion des erreurs de connexion
  test('06 - Login with invalid credentials', async ({ page }) => {
    await page.goto('http://127.0.0.1:5173/login');
    await page.waitForLoadState('networkidle');
    
    // Essayer avec un email invalide
    await page.fill('input[type="email"]', 'invalid@example.com');
    await page.fill('input[type="password"]', 'wrongpassword');
    
    await page.click('button[type="submit"]');
    
    // Attendre l'affichage de l'erreur
    await page.waitForTimeout(1000);
    
    // Vérifier qu'on est toujours sur la page de login
    await expect(page).toHaveURL(/login/);
    
    // Vérifier le message d'erreur (optionnel)
    // await expect(page.locator('.error')).toBeVisible();
  });
});

test.describe('EduNova Connection Tests', () => {
  test('07 - Should verify backend connection', async ({ page, request }) => {
    // Tester la connexion directe au backend
    const response = await request.get('http://127.0.0.1:8017/health');
    
    expect(response.ok()).toBeTruthy();
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data.status).toBe('ok');
  });
  
  test('08 - Should verify CORS headers', async ({ page, request }) => {
    // Tester les headers CORS
    const response = await request.get('http://127.0.0.1:8017/health', {
      headers: {
        'Origin': 'http://127.0.0.1:5173'
      }
    });
    
    expect(response.ok()).toBeTruthy();
    
    // Vérifier les headers CORS
    const access_control_origin = response.headers()['access-control-allow-origin'];
    expect(access_control_origin).toContain('http://127.0.0.1:5173');
  });
});
