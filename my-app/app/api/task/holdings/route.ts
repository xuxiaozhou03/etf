import { generateHoldingsInfo } from "@/services/reptile/task";
import { NextResponse } from "next/server";

export const GET = async () => {
  await generateHoldingsInfo();
  return NextResponse.json({ message: "ETFs info generation done" });
};
