import { Task } from "../utils/runTask";

export const getEtfCalculatorTask = (code: string): Task => ({
  name: `calculator_${code}`,
  run: async () => {},
});
