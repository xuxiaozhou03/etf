import { getEtfList } from "@/services/data/get_etf_list";
import { NextResponse } from "next/server";

export const GET = async () => {
  const list = await getEtfList();
  return NextResponse.json({
    data: list,
  });
};
