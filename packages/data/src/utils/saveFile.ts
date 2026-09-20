import fs from "fs";
import path from "path";

export const saveFile = (name: string, data: unknown) => {
  fs.writeFileSync(path.resolve(name), JSON.stringify(data));
};

export const getFile = <T = any>(name: string) => {
  const text = fs.readFileSync(path.resolve(name), {
    encoding: "utf-8",
  });
  try {
    return JSON.parse(text) as T;
  } catch {
    return undefined;
  }
};
