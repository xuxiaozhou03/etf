import { prisma } from "@quant-backtest/db";
import { shouldSkipAfterCutoff } from "./shouldSkipAfterCutoff";

export interface Task {
  name: string;
  run: () => Promise<void>;
}

export const runTask = async (task: Task): Promise<void> => {
  console.log(`Running task: ${task.name}`);
  try {
    const syncTask = await prisma.syncTaskRun.findFirst({
      where: {
        name: task.name,
      },
    });

    if (
      syncTask &&
      syncTask.status === "success" &&
      shouldSkipAfterCutoff(syncTask.finishedAt)
    ) {
      console.log(
        `Task ${task.name} has already been completed successfully. Skipping.`,
      );
      return;
    }

    await task.run();
    console.log(`Task ${task.name} completed successfully.`);
    await prisma.syncTaskRun.upsert({
      where: { name: task.name },
      update: {
        status: "success",
        finishedAt: new Date(),
      },
      create: {
        name: task.name,
        status: "success",
        finishedAt: new Date(),
      },
    });
  } catch (error) {
    console.error(`Task ${task.name} failed with error:`, error);
    throw error;
  }
};
