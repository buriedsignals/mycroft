// Run against a locally served site; see CONTRIBUTING.md for browser setup.
const assert = require('node:assert/strict');
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({
    ...(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {}),
  });
  try {
    for (const mode of [
      { name: 'phone', width: 390, touch: true },
      { name: 'small phone', width: 320, touch: true },
      { name: 'tablet', width: 1024, touch: true },
      { name: 'desktop', width: 1440, touch: false },
      { name: 'reduced motion', width: 390, touch: true, reduced: true },
    ]) {
      const page = await browser.newPage({
        viewport: { width: mode.width, height: 844 },
        hasTouch: mode.touch,
        isMobile: mode.touch,
        reducedMotion: mode.reduced ? 'reduce' : 'no-preference',
      });
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.goto(process.env.SITE_URL || 'http://127.0.0.1:8765');
      await page.evaluate(() => document.fonts.ready);
      if (!mode.reduced) await page.locator('#layer-front').waitFor();
      const result = await page.evaluate(() => {
        const text = document.querySelector('.hero__bottom');
        const top = text.getBoundingClientRect().top;
        // No animation frame can run between these operations. Native text
        // must move even while the animation's main-thread work is delayed.
        window.scrollTo(0, 300);
        return { delta: top - text.getBoundingClientRect().top, y: scrollY,
          width: innerWidth, scrollWidth: document.documentElement.scrollWidth };
      });
      if (mode.touch) {
        assert.equal(result.y, 300, mode.name + ': scroll must reach 300px');
        assert.ok(Math.abs(result.delta - result.y) < 1,
          mode.name + ': text must scroll without waiting for an animation frame');
      }
      assert.ok(result.scrollWidth <= result.width, mode.name + ': horizontal overflow');
      await page.setViewportSize({ width: mode.width, height: 700 });
      await page.waitForTimeout(150);
      assert.equal(await page.getByRole('button', { name: /gather|release the papers/i }).count(), 0);
      assert.deepEqual(errors, [], mode.name + ': browser errors');
      if (!mode.reduced) {
        await page.evaluate(() => scrollBy(0, document.querySelector('#what').getBoundingClientRect().top - 120));
        await page.waitForTimeout(1200);
        // Freeze the live scene so removing a transparent layer is pixel-stable.
        await page.evaluate(() => { window.requestAnimationFrame = () => 0; });
        await page.waitForTimeout(100);
        const withForeground = await page.screenshot({ animations: 'disabled' });
        await page.locator('#layer-front').evaluate(el => { el.style.visibility = 'hidden'; });
        const withoutForeground = await page.screenshot({ animations: 'disabled' });
        assert.ok(withForeground.equals(withoutForeground),
          mode.name + ': hero/body newspapers must render behind the document, without section masks');
        await page.locator('#layer-front').evaluate(el => { el.style.visibility = ''; });
      }
      await page.waitForTimeout(1200);
      await page.screenshot({ path: '/tmp/mycroft-' + mode.name.replaceAll(' ', '-') + '.png' });
      await page.close();
      console.log(mode.name + ': OK');
    }
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
