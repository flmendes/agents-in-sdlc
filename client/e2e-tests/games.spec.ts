import { test, expect } from '@playwright/test';

test.describe('Game Listing and Navigation', () => {
  test('should display games with titles on index page', async ({ page }) => {
    await page.goto('/');
    
    // Wait for the games to load
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
    
    // Check that games are displayed
    const gameCards = page.locator('[data-testid="game-card"]');
    
    // Wait for at least one game card to be visible
    await expect(gameCards.first()).toBeVisible();
    
    // Check that we have at least one game
    const gameCount = await gameCards.count();
    expect(gameCount).toBeGreaterThan(0);
    
    // Check that each game card has a title
    const firstGameCard = gameCards.first();
    await expect(firstGameCard.locator('[data-testid="game-title"]')).toBeVisible();
    
    // Verify that game titles are not empty
    const gameTitle = await firstGameCard.locator('[data-testid="game-title"]').textContent();
    expect(gameTitle?.trim()).toBeTruthy();
  });

  test('should navigate to correct game details page when clicking on a game', async ({ page }) => {
    await page.goto('/');
    
    // Wait for games to load
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
    
    // Get the first game card and its data attributes
    const firstGameCard = page.locator('[data-testid="game-card"]').first();
    const gameId = await firstGameCard.getAttribute('data-game-id');
    const gameTitle = await firstGameCard.getAttribute('data-game-title');
    
    // Click on the first game
    await firstGameCard.click();
    
    // Verify we're on the correct game details page
    await expect(page).toHaveURL(`/game/${gameId}`);
    
    // Verify the game details page loads
    await page.waitForSelector('[data-testid="game-details"]', { timeout: 10000 });
    
    // Verify the title matches what we clicked on
    const detailsTitle = page.locator('[data-testid="game-details-title"]');
    await expect(detailsTitle).toHaveText(gameTitle || '');
  });

  test('should display game details with all required information', async ({ page }) => {
    // Navigate to a specific game (we'll use game ID 1 as an example)
    await page.goto('/game/1');
    
    // Wait for game details to load
    await page.waitForSelector('[data-testid="game-details"]', { timeout: 10000 });
    
    // Check that the game title is present and not empty
    const gameTitle = page.locator('[data-testid="game-details-title"]');
    await expect(gameTitle).toBeVisible();
    const titleText = await gameTitle.textContent();
    expect(titleText?.trim()).toBeTruthy();
    
    // Check that the game description is present and not empty
    const gameDescription = page.locator('[data-testid="game-details-description"]');
    await expect(gameDescription).toBeVisible();
    const descriptionText = await gameDescription.textContent();
    expect(descriptionText?.trim()).toBeTruthy();
    
    // Check that either publisher or category (or both) are present
    const publisherExists = await page.locator('[data-testid="game-details-publisher"]').isVisible();
    const categoryExists = await page.locator('[data-testid="game-details-category"]').isVisible();
    expect(publisherExists && categoryExists).toBeTruthy();
    
    // If publisher exists, check it has content
    if (publisherExists) {
      const publisherText = await page.locator('[data-testid="game-details-publisher"]').textContent();
      expect(publisherText?.trim()).toBeTruthy();
    }
    
    // If category exists, check it has content
    if (categoryExists) {
      const categoryText = await page.locator('[data-testid="game-details-category"]').textContent();
      expect(categoryText?.trim()).toBeTruthy();
    }
  });

  test('should display a button to back the game', async ({ page }) => {
    await page.goto('/game/1');
    
    // Wait for game details to load
    await page.waitForSelector('[data-testid="game-details"]', { timeout: 10000 });
    
    // Check that the back game button is present
    const backButton = page.locator('[data-testid="back-game-button"]');
    await expect(backButton).toBeVisible();
    await expect(backButton).toContainText('Support This Game');
    
    // Verify the button is clickable
    await expect(backButton).toBeEnabled();
  });

  test('should be able to navigate back to home from game details', async ({ page }) => {
    await page.goto('/game/1');
    
    // Wait for the page to load
    await page.waitForSelector('[data-testid="game-details"]', { timeout: 10000 });
    
    // Find and click the back to all games link
    const backLink = page.locator('a:has-text("Back to all games")');
    await expect(backLink).toBeVisible();
    await backLink.click();
    
    // Verify we're back on the home page
    await expect(page).toHaveURL('/');
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
  });

  test('should handle navigation to non-existent game gracefully', async ({ page }) => {
    // Navigate to a game that doesn't exist
    await page.goto('/game/99999');
    
    // The page should load without crashing
    // Check if there's an error message or if it handles gracefully
    await page.waitForTimeout(3000);
    
    // The page should either show an error or handle it gracefully
    // We expect the page to not crash and still have a valid title
    await expect(page).toHaveTitle(/Game Details - Tailspin Toys/);
  });
});

test.describe('Game Pagination', () => {
  test('should display pagination controls when there are multiple pages', async ({ page }) => {
    await page.goto('/');
    
    // Wait for games to load
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
    
    // Check that pagination controls are visible
    const paginationControls = page.locator('[data-testid="pagination-controls"]');
    await expect(paginationControls).toBeVisible();
    
    // Check for pagination elements
    await expect(page.locator('[data-testid="prev-page-button"]')).toBeVisible();
    await expect(page.locator('[data-testid="next-page-button"]')).toBeVisible();
    await expect(page.locator('[data-testid="page-info"]')).toBeVisible();
    await expect(page.locator('[data-testid="goto-page-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="goto-page-button"]')).toBeVisible();
    await expect(page.locator('[data-testid="page-number-button"]')).toBeVisible();
  });

  test('should navigate between pages using next/previous buttons', async ({ page }) => {
    await page.goto('/');
    
    // Wait for games to load
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
    
    // Check we're on page 1
    await expect(page.locator('[data-testid="page-info"]')).toContainText('Page 1 of');
    
    // Previous button should be disabled on first page
    await expect(page.locator('[data-testid="prev-page-button"]')).toBeDisabled();
    
    // Click next button
    await page.locator('[data-testid="next-page-button"]').click();
    
    // Wait for page to load
    await page.waitForTimeout(1000);
    
    // Check we're now on page 2
    await expect(page.locator('[data-testid="page-info"]')).toContainText('Page 2 of');
    
    // URL should be updated
    await expect(page).toHaveURL('/?page=2');
    
    // Previous button should now be enabled
    await expect(page.locator('[data-testid="prev-page-button"]')).toBeEnabled();
    
    // Click previous button to go back
    await page.locator('[data-testid="prev-page-button"]').click();
    
    // Wait for page to load
    await page.waitForTimeout(1000);
    
    // Check we're back on page 1
    await expect(page.locator('[data-testid="page-info"]')).toContainText('Page 1 of');
    await expect(page).toHaveURL('/');
  });

  test('should navigate to specific page using page number buttons', async ({ page }) => {
    await page.goto('/');
    
    // Wait for games to load
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
    
    // Find page 2 button and click it
    const page2Button = page.locator('[data-testid="page-number-button"][data-page="2"]');
    await expect(page2Button).toBeVisible();
    await page2Button.click();
    
    // Wait for page to load
    await page.waitForTimeout(1000);
    
    // Check we're on page 2
    await expect(page.locator('[data-testid="page-info"]')).toContainText('Page 2 of');
    await expect(page).toHaveURL('/?page=2');
  });

  test('should navigate using go-to-page input', async ({ page }) => {
    await page.goto('/');
    
    // Wait for games to load
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
    
    // Type page number in input
    await page.locator('[data-testid="goto-page-input"]').fill('2');
    
    // Click go button
    await page.locator('[data-testid="goto-page-button"]').click();
    
    // Wait for page to load
    await page.waitForTimeout(1000);
    
    // Check we're on page 2
    await expect(page.locator('[data-testid="page-info"]')).toContainText('Page 2 of');
    await expect(page).toHaveURL('/?page=2');
    
    // Input should be cleared
    await expect(page.locator('[data-testid="goto-page-input"]')).toHaveValue('');
  });

  test('should navigate using go-to-page input with enter key', async ({ page }) => {
    await page.goto('/');
    
    // Wait for games to load
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
    
    // Type page number and press enter
    await page.locator('[data-testid="goto-page-input"]').fill('2');
    await page.locator('[data-testid="goto-page-input"]').press('Enter');
    
    // Wait for page to load
    await page.waitForTimeout(1000);
    
    // Check we're on page 2
    await expect(page.locator('[data-testid="page-info"]')).toContainText('Page 2 of');
    await expect(page).toHaveURL('/?page=2');
  });

  test('should support direct URL navigation to specific pages', async ({ page }) => {
    // Navigate directly to page 2
    await page.goto('/?page=2');
    
    // Wait for games to load
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
    
    // Check we're on page 2
    await expect(page.locator('[data-testid="page-info"]')).toContainText('Page 2 of');
    
    // Check that pagination controls show correct state
    await expect(page.locator('[data-testid="prev-page-button"]')).toBeEnabled();
  });

  test('should display correct game count information', async ({ page }) => {
    await page.goto('/');
    
    // Wait for games to load
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
    
    // Check the game count display format
    const gameCountText = await page.locator('text=/Showing \\d+-\\d+ of \\d+ games/').textContent();
    expect(gameCountText).toBeTruthy();
    
    // Navigate to page 2
    await page.goto('/?page=2');
    await page.waitForSelector('[data-testid="games-grid"]', { timeout: 10000 });
    
    // Check page 2 game count
    const page2CountText = await page.locator('text=/Showing \\d+-\\d+ of \\d+ games/').textContent();
    expect(page2CountText).toBeTruthy();
  });

  test('should handle invalid page numbers gracefully', async ({ page }) => {
    // Try to navigate to a page that doesn't exist
    await page.goto('/?page=999');
    
    // Wait for the page to load
    await page.waitForTimeout(3000);
    
    // The page should load without crashing and show no games
    // or redirect to a valid page
    await expect(page).toHaveTitle('Tailspin Toys - Crowdfunding your new favorite game!');
  });
});
