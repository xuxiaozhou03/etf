// PrismaClient 惰性单例。业务读写都在本层之外：
//   读服务（DataService）在 @quant-backtest/data，写库（DataWriter / PeriodReturnCalculator）在 @quant-backtest/crawler。
// 使用前先 generate：pnpm --filter @quant-backtest/db prisma:generate（schema 见 src/prisma/schema.prisma）。

import { PrismaClient } from "@prisma/client";

let _prisma: PrismaClient | undefined;

/** 共享 PrismaClient（首次调用才实例化，避免模块加载时就要求 DATABASE_URL） */
function getPrisma(): PrismaClient {
  if (!_prisma) _prisma = new PrismaClient();
  return _prisma;
}

export const prisma = getPrisma();
