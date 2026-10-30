const assert = require('node:assert/strict');
const browserType = require('playwright')[process.env.BROWSER_ENGINE || 'chromium'];

(async () => {
  const browser = await browserType.launch({
    ...(process.env.BROWSER_PATH || process.env.CHROME_PATH
      ? { executablePath: process.env.BROWSER_PATH || process.env.CHROME_PATH } : {}),
  });
  try {
    for (const width of [320, 390, 1440]) {
      const touch = width < 768;
      const page = await browser.newPage({ viewport: { width, height: 844 }, hasTouch: touch, isMobile: touch });
      const errors = [];
      page.on('pageerror', e => errors.push(e.message));
      await page.goto(process.env.SITE_URL || 'http://127.0.0.1:8765');
      await page.locator('#layer-front').waitFor();
      await page.locator('.skills-index__description').first().waitFor({ state: 'attached' });
      await page.evaluate(() => document.fonts.ready);
      await page.waitForTimeout(1500);
      await page.screenshot({ path: `/tmp/mycroft-hero-${width}.png` });
      assert.equal(await page.getByRole('button', { name: /gather|release the papers/i }).count(), 0);
      if (touch) {
        const partners = await page.evaluate(() => {
          const band = document.querySelector('.hero__partners');
          const label = band.querySelector('span');
          const logos = [...band.querySelectorAll('a')].map(a => a.getBoundingClientRect().toJSON());
          const r = label.getBoundingClientRect();
          return { center: r.left + r.width / 2, logos, border: getComputedStyle(band).borderTopWidth };
        });
        assert.ok(Math.abs(partners.center - width / 2) < 1, 'Partnership label must be centered');
        assert.ok(Math.abs(partners.logos[0].top - partners.logos[1].top) < 1, 'Partner logos must share a row');
        assert.equal(partners.border, '0px', 'Remove the stray rule above the partnership');
      }
      const descriptions = await page.locator('.skills-index__description').allTextContents();
      assert.equal(descriptions.length, 4);
      assert.ok(descriptions.every(text => text.length > 15 && text.length <= 140), 'Catalog summaries must be concise');
      for (const selector of ['.hero__partners a', '.hero__lede .pill', '#what .pill']) {
        const links = page.locator(selector);
        for (let i = 0; i < await links.count(); i++) {
          const link = links.nth(i);
          assert.equal(await link.getAttribute('aria-controls'), 'tool-preview', 'Every pill needs a preview');
          const href = await link.getAttribute('href');
          // Desktop text is in a fixed CSS3D plane; scroll the document itself.
          await link.evaluate(e => scrollBy(0, e.getBoundingClientRect().top - innerHeight / 2));
          await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
          const popups = [];
          const onPopup = popup => popups.push(popup);
          page.on('popup', onPopup);
          if (touch) await link.tap(); else await link.hover();
          const preview = page.locator('#tool-preview');
          await preview.waitFor({ state: 'visible' });
          const destination = preview.getByRole('link');
          assert.equal(await destination.getAttribute('href'), href);
          assert.equal(popups.length, 0, 'Opening a preview must not navigate');
          if (touch) {
            await page.context().route(href, route => route.fulfill({ body: 'Preview destination' }));
            const popupEvent = page.waitForEvent('popup');
            await destination.tap();
            const popup = await popupEvent;
            await popup.waitForLoadState();
            assert.equal(popup.url(), href, 'Preview media must link to the destination');
            await popup.close();
            await preview.getByRole('button', { name: 'Close' }).tap();
          } else {
            await page.keyboard.press('Escape');
          }
          page.off('popup', onPopup);
        }
      }
      if (touch) {
        await page.evaluate(() => scrollTo(0, document.documentElement.scrollHeight));
        await page.waitForTimeout(200);
        const footer = await page.locator('.bs-property-signal__content').evaluate(e => ({
          position: getComputedStyle(e).position, bottom: e.getBoundingClientRect().bottom,
        }));
        assert.equal(footer.position, 'fixed', 'Native mobile footer must anchor to the viewport');
        assert.ok(Math.abs(footer.bottom - 844) < 1);
        await page.evaluate(() => scrollBy(0, -80));
        await page.waitForTimeout(200);
        const bottom = await page.locator('.bs-property-signal__content').evaluate(e => e.getBoundingClientRect().bottom);
        assert.ok(Math.abs(bottom - 844) < 1, 'Scrolling back must not expose space below the footer');
        assert.equal(await page.locator('html').evaluate(e => getComputedStyle(e).backgroundColor), 'rgb(22, 25, 27)');
      }
      assert.deepEqual(errors, []);
      await page.screenshot({ path: `/tmp/mycroft-details-${width}.png` });
      await page.close();
      console.log(width + 'px mobile details: OK');
    }
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
