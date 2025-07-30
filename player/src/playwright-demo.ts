// playwright-demo.ts
// 使用 Playwright 爬取示例

import fs from "fs";
import { chromium } from "playwright";

(async () => {
  // 启动浏览器
  const browser = await chromium.launch();
  const page = await browser.newPage();

  // 访问页面
  await page.goto("https://mp.weixin.qq.com/s/6P52-4qd5eau2LGkbcIaBQ");

  // 获取页面内容
  const pageContent = await page.$eval("#page-content", (el) => el.innerHTML);
  console.log("page-content 内容:", pageContent);
  fs.writeFileSync("page-content.html", pageContent);

  // 关闭浏览器
  await browser.close();
})();
