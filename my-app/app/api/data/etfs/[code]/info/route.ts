import { getEtfInfo } from "@/services/data/get_etf_info";
import { NextResponse } from "next/server";

export async function GET(
  request: Request,
  { params }: { params: { code: string } }
) {
  const code = await params.code;
  const info = await getEtfInfo(code || "159278");
  return NextResponse.json(info);
}
