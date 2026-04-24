export async function run(page) {
  await page.goto("https://news.ycombinator.com/news", {
    waitUntil: "domcontentloaded",
  });

  const stories = await page.$$eval(".titleline > a", (links) =>
    links.slice(0, 5).map((link) => ({
      title: link.textContent,
      url: link.href,
    })),
  );

  return Response.json({ count: stories.length, stories });
}
