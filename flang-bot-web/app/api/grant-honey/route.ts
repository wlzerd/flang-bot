import { NextResponse } from 'next/server'
import { addHoney, getUser } from '@/lib/db'

export async function POST(req: Request) {
  const data = await req.json()
  const userId = String(data.userId || '')
  const amount = Number(data.amount)
  if (!userId || !Number.isFinite(amount)) {
    return NextResponse.json({ error: 'invalid parameters' }, { status: 400 })
  }
  const user = getUser(userId)
  if (!user) {
    return NextResponse.json({ error: 'user not found' }, { status: 404 })
  }
  addHoney(userId, amount)
  return NextResponse.json({ success: true })
}
