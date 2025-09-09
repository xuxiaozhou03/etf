import { NextResponse } from "next/server";
import { fetchAllEtfList } from "@etf/data";

export const GET = async () => {
  const list = await fetchAllEtfList();
  return NextResponse.json(list);
};
