import { NextResponse } from 'next/server'
import { getAdventureProbabilities, setAdventureProbabilities } from '@/lib/db'

export async function GET() {
  const probs = getAdventureProbabilities()
  return NextResponse.json(probs)
}

export async function POST(req: Request) {
  const data = await req.json()
  const success = Number(data.success)
  const fail = Number(data.fail)
  const normal = Number(data.normal)
  if (![success, fail, normal].every(n => Number.isFinite(n))) {
    return NextResponse.json({ error: 'invalid parameters' }, { status: 400 })
  }
  setAdventureProbabilities(success, fail, normal)
  return NextResponse.json({ success: true })
}
