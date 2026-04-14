import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function GET(req: NextRequest) {
    const { searchParams } = new URL(req.url);
    const days = searchParams.get("days_ahead") ?? "7";
    const upstream = await fetch(`${API_URL}/slots?days_ahead=${days}`);
    const data = await upstream.json();
    return NextResponse.json(data, { status: upstream.status });
}
