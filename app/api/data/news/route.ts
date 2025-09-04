import { handleNew } from "@/services/reptile/news";
import { NextResponse } from "next/server";

export const GET = async () => {
  const data = await handleNew(
    "https://finance.eastmoney.com/a/202509043504820411.html"
  );
  return NextResponse.json(data);
};
