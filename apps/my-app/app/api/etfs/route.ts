import { NextResponse } from "next/server";
import { fetchScaleChange } from "@etf/data";

export const GET = async () => {
  const scaleChange = await fetchScaleChange("159322");
  return NextResponse.json({ scaleChange });
};
