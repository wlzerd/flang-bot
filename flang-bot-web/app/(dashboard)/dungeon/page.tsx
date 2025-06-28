"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Slider } from "@/components/ui/slider"
import { Checkbox } from "@/components/ui/checkbox"

export default function DungeonPage() {
  const [difficulty, setDifficulty] = useState([50])

  async function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const success = difficulty[0]
    const fail = 100 - success
    await fetch('/api/adventure-probabilities', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ success, fail, normal: 0 })
    })
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center">
        <h1 className="text-lg font-semibold md:text-2xl">던전 조정</h1>
      </div>
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <CardTitle>던전 설정</CardTitle>
          <CardDescription>모험(던전)의 세부 설정을 조정합니다.</CardDescription>
        </CardHeader>
        <CardContent>
          <form className="grid gap-6" onSubmit={submit}>
            <div className="grid gap-3">
              <Label htmlFor="difficulty">난이도</Label>
              <Slider id="difficulty" value={difficulty} onValueChange={setDifficulty} max={100} step={1} />
              <div className="flex justify-between text-sm text-muted-foreground">
                <span>쉬움</span>
                <span>보통</span>
                <span>어려움</span>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="min-reward">최소 보상</Label>
                <Input id="min-reward" type="number" placeholder="예: 100" />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="max-reward">최대 보상</Label>
                <Input id="max-reward" type="number" placeholder="예: 500" />
              </div>
            </div>
            <div className="grid gap-2">
              <Label>특수 이벤트</Label>
              <div className="flex items-center space-x-2">
                <Checkbox id="rare-mob-event" />
                <label
                  htmlFor="rare-mob-event"
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  희귀 몬스터 출현 이벤트 활성화
                </label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox id="bonus-reward-event" />
                <label
                  htmlFor="bonus-reward-event"
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  보너스 보상 이벤트 활성화
                </label>
              </div>
            </div>
            <Button type="submit">설정 저장</Button>
          </form>
        </CardContent>
        <CardFooter className="border-t px-6 py-4" />
      </Card>
    </div>
  )
}
