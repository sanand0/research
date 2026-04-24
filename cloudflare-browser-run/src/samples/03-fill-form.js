export async function run(page) {
  await page.goto("https://www.wikipedia.org/", {
    waitUntil: "domcontentloaded",
  });
  await page.type("#searchInput", "Cloudflare");
  await Promise.all([
    page.waitForNavigation({ waitUntil: "domcontentloaded" }),
    page.click("button[type='submit']"),
  ]);

  const result = await page.evaluate(() => ({
    title: document.title,
    heading: document.querySelector("#firstHeading")?.textContent ?? "",
    url: location.href,
  }));

  return Response.json(result);
}
