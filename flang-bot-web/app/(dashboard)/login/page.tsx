"use client"

import type React from "react"

import { useRouter } from "next/navigation"
import { Bot } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export default function LoginPage() {
  const router = useRouter()

  const handleLogin = (event: React.FormEvent) => {
    event.preventDefault()
    // 실제 애플리케이션에서는 여기서 인증 로직을 처리합니다.
    // 예: const response = await fetch('/api/login', { ... });
    // 로그인이 성공했다고 가정하고 대시보드로 리디렉션합니다.
    router.push("/")
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-muted/40">
      <Card className="w-full max-w-sm">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            <Bot className="h-8 w-8" />
          </div>
          <CardTitle className="text-2xl">Flang-Bot 관리자 로그인</CardTitle>
          <CardDescription>계속하려면 아이디와 비밀번호를 입력하세요.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleLogin} className="grid gap-4">
            <div className="grid gap-2">
              <Label htmlFor="username">아이디</Label>
              <Input id="username" type="text" placeholder="admin" required />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="password">비밀번호</Label>
              <Input id="password" type="password" required />
            </div>
            <Button type="submit" className="w-full mt-2">
              로그인
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
