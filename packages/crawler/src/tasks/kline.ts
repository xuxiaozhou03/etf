import { Task } from "../utils/runTask";

export const getEtfKlineTask = (code: string): Task => ({
  name: `kline_${code}`,
  run: async () => {},
});

const fetchKline = async () => {};
