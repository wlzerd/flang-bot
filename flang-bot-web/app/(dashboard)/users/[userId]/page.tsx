"use client"

import * as React from "react"
import Image from "next/image"
import Link from "next/link"
import { ArrowLeft, Coins, History } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/hooks/use-toast"

// 샘플 데이터입니다. 실제로는 API를 통해 받아오게 됩니다.
const usersData = {
  USR001: {
    id: "USR001",
    name: "모험적인유저",
    avatar: "/placeholder.svg?height=96&width=96",
    joinedDate: "2025-01-15",
    points: 1250,
    status: "active",
    activityLogs: [
      { id: "L01", timestamp: "2025-06-29 10:30:15", command: "/모험", details: "성공 - 50 꿀 획득" },
      { id: "L02", timestamp: "2025-06-28 10:20:11", command: "/모험", details: "실패 - 20 꿀 잃음" },
      { id: "L03", timestamp: "2025-06-28 09:05:43", command: "/꿀단지", details: "보유 꿀 확인" },
    ],
    pointHistory: [
      { id: "P01", timestamp: "2025-06-29 10:30:15", description: "모험 성공 보상", change: "+50", balance: 1250 },
      {
        id: "P02",
        timestamp: "2025-06-29 10:28:45",
        description: "관대한기부자에게 선물 받음",
        change: "+100",
        balance: 1200,
      },
      { id: "P03", timestamp: "2025-06-28 10:20:11", description: "모험 실패", change: "-20", balance: 1100 },
      { id: "P04", timestamp: "2025-06-27 15:00:00", description: "이벤트 참가 보상", change: "+1000", balance: 1120 },
      { id: "P05", timestamp: "2025-01-15 12:00:00", description: "가입 축하 꿀", change: "+20", balance: 20 },
    ],
  },
  USR002: {
    id: "USR002",
    name: "관대한기부자",
    avatar: "/placeholder.svg?height=96&width=96",
    joinedDate: "2025-02-20",
    points: 500,
    status: "active",
    activityLogs: [
      { id: "L04", timestamp: "2025-06-29 10:28:45", command: "/허니선물", details: "모험적인유저에게 100 꿀 선물" },
    ],
    pointHistory: [
      {
        id: "P06",
        timestamp: "2025-06-29 10:28:45",
        description: "모험적인유저에게 선물",
        change: "-100",
        balance: 500,
      },
      {
        id: "P07",
        timestamp: "2025-06-27 10:15:55",
        description: "관리자로부터 지급받음",
        change: "+1000",
        balance: 600,
      },
    ],
  },
  USR003: {
    id: "USR003",
    name: "새로운참가자",
    avatar: "/placeholder.svg?height=96&width=96",
    joinedDate: "2025-06-28",
    points: 100,
    status: "active",
    activityLogs: [{ id: "L05", timestamp: "2025-06-28 10:25:02", command: "/가입", details: "신규 가입 완료" }],
    pointHistory: [
      { id: "P08", timestamp: "2025-06-28 10:25:02", description: "가입 축하 꿀", change: "+100", balance: 100 },
    ],
  },
  USR004: {
    id: "USR004",
    name: "관리자마스터",
    avatar: "/placeholder.svg?height=96&width=96",
    joinedDate: "2024-12-10",
    points: 99999,
    status: "active",
    activityLogs: [
      { id: "L06", timestamp: "2025-06-27 10:15:55", command: "/지급", details: "관대한기부자에게 1000 꿀 지급" },
    ],
    pointHistory: [],
  },
  USR005: {
    id: "USR005",
    name: "휴면계정",
    avatar: "/placeholder.svg?height=96&width=96",
    joinedDate: "2025-03-05",
    points: 50,
    status: "inactive",
    activityLogs: [],
    pointHistory: [],
  },
}

export default function UserDetailPage({ params }: { params: { userId: string } }) {
  const { toast } = useToast()
  const [amount, setAmount] = React.useState("")
  const [reason, setReason] = React.useState("")
  const user = usersData[params.userId as keyof typeof usersData]

  const handlePointAdjustment = (type: "give" | "deduct") => {
    const pointAmount = Number.parseInt(amount, 10)
    if (isNaN(pointAmount) || pointAmount <= 0) {
      toast({
        title: "오류",
        description: "유효한 포인트를 입력해주세요.",
        variant: "destructive",
      })
      return
    }

    if (!reason.trim()) {
      toast({
        title: "오류",
        description: "지급/차감 사유를 입력해주세요.",
        variant: "destructive",
      })
      return
    }

    const actionText = type === "give" ? "지급" : "차감"
    const description = `${user.name}님에게 ${pointAmount.toLocaleString()} 꿀을 ${actionText}했습니다. (사유: ${reason})`

    toast({
      title: `포인트 ${actionText} 완료`,
      description: description,
    })

    // 실제 애플리케이션에서는 여기서 API를 호출하여 서버의 데이터를 업데이트합니다.
    // 예: await updateUserPoints(user.id, type === 'give' ? pointAmount : -pointAmount, reason);

    // 폼 초기화
    setAmount("")
    setReason("")
  }

  if (!user) {
    return (
      <div className="flex flex-col items-center justify-center h-full">
        <h2 className="text-2xl font-bold mb-4">사용자를 찾을 수 없습니다.</h2>
        <Link href="/users">
          <Button>사용자 목록으로 돌아가기</Button>
        </Link>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-4">
        <Link href="/users">
          <Button variant="outline" size="icon" className="h-7 w-7 bg-transparent">
            <ArrowLeft className="h-4 w-4" />
            <span className="sr-only">뒤로</span>
          </Button>
        </Link>
        <h1 className="flex-1 shrink-0 whitespace-nowrap text-xl font-semibold tracking-tight sm:grow-0">
          {user.name}
        </h1>
        <Badge variant={user.status === "active" ? "secondary" : "outline"} className="ml-auto sm:ml-0">
          {user.status === "active" ? "활동중" : "비활성"}
        </Badge>
      </div>
      <div className="grid gap-6 md:grid-cols-[1fr_2fr] lg:grid-cols-[1fr_3fr]">
        <div className="flex flex-col gap-6">
          <Card>
            <CardHeader>
              <CardTitle>프로필</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col items-center gap-4 text-sm">
              <Image
                src={user.avatar || "/placeholder.svg"}
                width={96}
                height={96}
                alt={`${user.name}'s avatar`}
                className="rounded-full"
              />
              <div className="grid gap-1 text-center">
                <div className="font-semibold text-xl">{user.name}</div>
                <div className="text-sm text-muted-foreground">ID: {user.id}</div>
              </div>
              <Separator />
              <div className="w-full grid grid-cols-[auto_1fr] gap-x-4 gap-y-2">
                <span className="text-muted-foreground">가입일</span>
                <span className="text-right font-medium">{user.joinedDate}</span>
                <span className="text-muted-foreground">보유 꿀</span>
                <span className="text-right font-medium">{user.points.toLocaleString()} 꿀</span>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>포인트 조정</CardTitle>
              <CardDescription>관리자가 사용자에게 포인트를 직접 지급하거나 차감합니다.</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-4">
              <div className="grid gap-2">
                <Label htmlFor="points-amount">조정할 꿀</Label>
                <Input
                  id="points-amount"
                  type="number"
                  placeholder="예: 100"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="points-reason">사유</Label>
                <Textarea
                  id="points-reason"
                  placeholder="예: 이벤트 보상"
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                />
              </div>
            </CardContent>
            <CardFooter className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => handlePointAdjustment("deduct")}>
                차감
              </Button>
              <Button onClick={() => handlePointAdjustment("give")}>지급</Button>
            </CardFooter>
          </Card>
        </div>
        <div className="flex flex-col gap-6">
          <Tabs defaultValue="activity">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="activity">
                <History className="mr-2 h-4 w-4" />
                활동 내역
              </TabsTrigger>
              <TabsTrigger value="points">
                <Coins className="mr-2 h-4 w-4" />
                포인트 내역
              </TabsTrigger>
            </TabsList>
            <TabsContent value="activity">
              <Card>
                <CardHeader>
                  <CardTitle>최근 활동 내역</CardTitle>
                  <CardDescription>사용자의 최근 봇 명령어 사용 기록입니다.</CardDescription>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>시간</TableHead>
                        <TableHead>명령어</TableHead>
                        <TableHead>세부 정보</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {user.activityLogs.length > 0 ? (
                        user.activityLogs.map((log) => (
                          <TableRow key={log.id}>
                            <TableCell className="text-muted-foreground">{log.timestamp}</TableCell>
                            <TableCell>
                              <Badge variant="outline">{log.command}</Badge>
                            </TableCell>
                            <TableCell>{log.details}</TableCell>
                          </TableRow>
                        ))
                      ) : (
                        <TableRow>
                          <TableCell colSpan={3} className="h-24 text-center">
                            활동 기록이 없습니다.
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </TabsContent>
            <TabsContent value="points">
              <Card>
                <CardHeader>
                  <CardTitle>포인트 변동 내역</CardTitle>
                  <CardDescription>사용자의 꿀(포인트) 획득 및 사용 기록입니다.</CardDescription>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>시간</TableHead>
                        <TableHead>내용</TableHead>
                        <TableHead>변동</TableHead>
                        <TableHead className="text-right">잔액</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {user.pointHistory.length > 0 ? (
                        user.pointHistory.map((entry) => (
                          <TableRow key={entry.id}>
                            <TableCell className="text-muted-foreground">{entry.timestamp}</TableCell>
                            <TableCell>{entry.description}</TableCell>
                            <TableCell className={entry.change.startsWith("+") ? "text-green-500" : "text-red-500"}>
                              {entry.change}
                            </TableCell>
                            <TableCell className="text-right">{entry.balance.toLocaleString()} 꿀</TableCell>
                          </TableRow>
                        ))
                      ) : (
                        <TableRow>
                          <TableCell colSpan={4} className="h-24 text-center">
                            포인트 변동 기록이 없습니다.
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  )
}
