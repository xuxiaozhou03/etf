import * as cheerio from "cheerio";
import { request } from "@/utils/request";

// 处理新闻
export const handleNew = async (url: string) => {
  const html = await request(url);
  const $ = cheerio.load(html);
  const lines: string[] = [];
  $("#ContentBody p").each((_, el) => {
    const line = $(el).text().trim();
    if (!line) {
      return;
    }
    lines.push(line);
  });
  return {
    lines,
    url,
  };
};
