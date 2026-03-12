const fs = require("fs");

// 读取 JSON 文件
const data = JSON.parse(fs.readFileSync("etfs.json", "utf-8"));

// 获取列名
const headers = ["name", "tracking", "assetSize"];

// 生成 CSV 内容
const csvRows = [];

// 添加表头
csvRows.push(headers.join(","));

// 添加数据行
for (const row of data.sort((a, b) => (a.assetSize < b.assetSize ? 1 : -1))) {
  const values = headers.map((header) => {
    const value =
      header === "name" ? row.name + "(" + row.code + ")" : row[header];
    // 处理包含逗号或引号的值
    if (
      typeof value === "string" &&
      (value.includes(",") || value.includes('"'))
    ) {
      return `"${value.replace(/"/g, '""')}"`;
    }
    return value;
  });
  csvRows.push(values.join(","));
}

// 写入 CSV 文件
fs.writeFileSync("etfs.csv", "\uFEFF" + csvRows.join("\n"), "utf-8");

console.log(`成功转换 ${data.length} 条记录到 etfs.csv`);
