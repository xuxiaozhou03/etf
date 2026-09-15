import { serve } from "@hono/node-server";
import { app } from "./app";

const port = Number(process.env.WEB_PORT ?? 3070);
const host = "0.0.0.0";

serve({ fetch: app.fetch, port, hostname: host }, (info) => {
  console.log(`[web] dashboard listening on http://${host}:${info.port}`);
});
