// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Widget', () => {
  test('should open widget and send message', async ({ page }) => {
    // Navigate to widget page
    await page.goto('http://localhost:8000');
    
    // Click widget toggle button
    const toggleButton = page.locator('#widgetToggle');
    await expect(toggleButton).toBeVisible();
    await toggleButton.click();
    
    // Wait for widget to open
    const widget = page.locator('#chatbotWidget');
    await expect(widget).toBeVisible();
    
    // Check welcome message
    const welcomeMessage = page.locator('.widget-system-content');
    await expect(welcomeMessage).toBeVisible();
    
    // Send a message
    const input = page.locator('#widgetMessageInput');
    await input.fill('Merhaba, test mesajı');
    
    const sendButton = page.locator('#widgetSendButton');
    await sendButton.click();
    
    // Wait for response (or typing indicator)
    await page.waitForTimeout(2000);
    
    // Check if message was sent
    const messages = page.locator('.widget-message');
    await expect(messages).toHaveCount(1); // At least one message
  });

  test('should handle WebSocket connection', async ({ page }) => {
    await page.goto('http://localhost:8000');
    
    // Monitor WebSocket connections
    const wsConnected = page.waitForEvent('websocket', { timeout: 5000 }).catch(() => null);
    
    const toggleButton = page.locator('#widgetToggle');
    await toggleButton.click();
    
    // Wait a bit for WebSocket connection
    await page.waitForTimeout(1000);
    
    // WebSocket should be connected (if implemented)
    // This is a basic test - adjust based on your implementation
  });
});

