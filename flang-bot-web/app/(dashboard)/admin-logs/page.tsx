import Image from "next/image"

import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

// 샘플 관리자 로그 데이터입니다. 실제로는 API를 통해 받아오게 됩니다.
const adminLogs = [
  {
    id: "ALOG001",
    timestamp: "2025-06-29 14:10:25",
    admin: {
      name: "관리자마스터",
      avatar: "/placeholder.svg?height=32&width=32",
    },
    targetUser: {
      name: "모험적인유저",
    },
    action: "포인트 지급",
    details: "1,000 꿀 (사유: 주간 이벤트 우승 보상)",
  },
  {
    id: "ALOG002",
    timestamp: "2025-06-29 11:05:11",
    admin: {
      name: "부관리자",
      avatar: "/placeholder.svg?height=32&width=32",
    },
    targetUser: {
      name: "관대한기부자",
    },
    action: "포인트 차감",
    details: "500 꿀 (사유: 시스템 오류로 인한 과지급 회수)",
  },
  {
    id: "ALOG003",
    timestamp: "2025-06-28 18:30:00",
    admin: {
      name: "관리자마스터",
      avatar: "/placeholder.svg?height=32&width=32",
    },
    targetUser: {
      name: "새로운참가자",
    },
    action: "포인트 지급",
    details: "200 꿀 (사유: 버그 제보 보상)",
  },
]

export default function AdminLogsPage() {
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
              {adminLogs.map((log) => (
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
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
