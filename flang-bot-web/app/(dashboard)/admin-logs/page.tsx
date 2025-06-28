"use client"

import Image from "next/image"
import * as React from "react"

import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

export default function AdminLogsPage() {
  const [logs, setLogs] = React.useState<any[]>([])

  React.useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/logs/admin`)
      .then((res) => res.json())
      .then((d) => setLogs(d))
      .catch((err) => console.error(err))
  }, [])

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center">
        <h1 className="text-lg font-semibold md:text-2xl">관리자 로그</h1>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>관리자 활동 기록</CardTitle>
          <CardDescription>포인트 지급, 차감 등 관리자 활동 내역입니다.</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="hidden sm:table-cell">시간</TableHead>
                <TableHead>관리자</TableHead>
                <TableHead>대상 유저</TableHead>
                <TableHead>작업</TableHead>
                <TableHead>세부 정보</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {logs.length > 0 ? (
                logs.map((log) => (
                  <TableRow key={log.id}>
                    <TableCell className="hidden sm:table-cell text-sm text-muted-foreground">{log.timestamp}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Image
                          src={log.admin.avatar || "/placeholder.svg"}
                          width={28}
                          height={28}
                          alt="Admin Avatar"
                          className="rounded-full"
                        />
                        <span className="font-medium">{log.admin.name}</span>
                      </div>
                    </TableCell>
                    <TableCell>{log.targetUser.name}</TableCell>
                    <TableCell>
                      <Badge variant={log.action.includes("지급") ? "default" : "destructive"}>{log.action}</Badge>
                    </TableCell>
                    <TableCell>{log.details}</TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={5} className="h-24 text-center">
                    기록이 없습니다.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
