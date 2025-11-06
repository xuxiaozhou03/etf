import Koa from "koa";
import Router from "@koa/router";
import { fetchEtfs } from "./services/stock-data/etfs";
import { fetchEtfInfo } from "./services/stock-data/etf/info";
import { reptileEtfAndInfo } from "./services/task/etfs";

const app = new Koa();
const router = new Router();

router.get("/", (ctx: Koa.Context) => {
  ctx.body = { message: "ETFs API1" };
});

router.get("/etfs", async (ctx: Koa.Context) => {
  const etfs = await fetchEtfs();
  ctx.body = etfs;
});
router.get("/etf/:code", async (ctx: Koa.Context) => {
  const etfInfo = await fetchEtfInfo(ctx.params.code);
  ctx.body = etfInfo;
});

router.get("/task", async (ctx: Koa.Context) => {
  const result = await reptileEtfAndInfo();
  ctx.body = result;
});

app.use(router.routes()).use(router.allowedMethods());

// Start server when invoked directly
if (require.main === module) {
  const port = process.env.PORT || 3012;
  app.listen(Number(port), () => {
    // eslint-disable-next-line no-console
    console.log(`Server listening on port ${port}`);
  });
}

export default app;
