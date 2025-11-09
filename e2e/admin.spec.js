// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Admin Panel', () => {
  test('should load admin dashboard', async ({ page }) => {
    // Navigate to admin panel
    await page.goto('http://localhost:8000/admin');
    
    // Check if sidebar is visible
    const sidebar = page.locator('.sidebar');
    await expect(sidebar).toBeVisible();
    
    // Check if dashboard stats are visible
    const stats = page.locator('.ai-card');
    await expect(stats).toHaveCount(4); // 4 stat cards
    
    // Check if chart is visible
    const chart = page.locator('#aiChart');
    await expect(chart).toBeVisible();
  });

  test('should navigate to chat management', async ({ page }) => {
    await page.goto('http://localhost:8000/admin');
    
    // Click on chat management link
    const chatLink = page.locator('text=Canlı Sohbetler');
    await chatLink.click();
    
    // Should navigate to chat page
    await page.waitForTimeout(500);
    // Add more assertions based on your implementation
  });

  test('should display metrics', async ({ page }) => {
    await page.goto('http://localhost:8000/admin');
    
    // Check if metrics are displayed
    const todayChats = page.locator('#todayChats');
    await expect(todayChats).toBeVisible();
    
    const avgResponseTime = page.locator('#avgResponseTime');
    await expect(avgResponseTime).toBeVisible();
  });
});

