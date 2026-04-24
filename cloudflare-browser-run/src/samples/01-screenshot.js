export async function run(page) {
  await page.goto("https://example.com", { waitUntil: "domcontentloaded" });

  const png = await page.screenshot();
  return new Response(png, {
    headers: { "content-type": "image/png" },
  });
}
