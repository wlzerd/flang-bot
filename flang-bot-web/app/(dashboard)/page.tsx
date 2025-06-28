"use client"

import { useEffect, useState } from "react"
import { UserGrowthChart } from "@/components/user-growth-chart"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Users, Database, UserPlus, Activity } from "lucide-react"

export default function DashboardPage() {
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalHoney: 0,
    joinedToday: 0,
    activeToday: 0,
  })

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/stats/overview`)
      .then((res) => res.json())
      .then((data) => setStats(data))
      .catch((err) => console.error(err))
  }, [])

  return (
    <>
      <div className="flex items-center">
        <h1 className="text-lg font-semibold md:text-2xl">홈</h1>
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 유저</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalUsers.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">서버에 가입한 전체 유저 수</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">총 꿀 유통량</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalHoney.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">모든 유저가 보유한 꿀의 총합</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">오늘 가입</CardTitle>
            <UserPlus className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">+{stats.joinedToday.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">오늘 새로 가입한 유저 수</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">오늘 활동 유저</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.activeToday.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">오늘 채팅을 1회 이상 사용한 유저</p>
          </CardContent>
        </Card>
      </div>
      <div className="w-full">
        <UserGrowthChart />
      </div>
    </>
  )
}
