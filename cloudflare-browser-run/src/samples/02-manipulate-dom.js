export async function run(page) {
  await page.goto("https://example.com", { waitUntil: "domcontentloaded" });
  await page.evaluate(() => {
    document.querySelector("h1").textContent = "Edited inside Browser Run";
    document.querySelector("p").textContent =
      "The Worker changed this DOM before capturing the page.";
    document.body.style.background = "#f6f1e8";
    document.body.style.borderTop = "12px solid #f48120";
  });

  const png = await page.screenshot();
  return new Response(png, {
    headers: { "content-type": "image/png" },
  });
}
