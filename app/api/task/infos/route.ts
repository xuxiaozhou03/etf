import { generateEtfsInfo } from "@/services/reptile/task";
import { NextResponse } from "next/server";

export const GET = async () => {
  await generateEtfsInfo();
  return NextResponse.json({ message: "ETFs info generation done" });
};
