"use client"

import * as React from "react"
import Image from "next/image"
import { CalendarIcon } from "lucide-react"
import { format } from "date-fns"
import type { DateRange } from "react-day-picker"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"

// 샘플 로그 데이터입니다. 실제로는 API를 통해 받아오게 됩니다.
const logs = [
  {
    id: "LOG001",
    timestamp: "2025-06-29 10:30:15",
    user: {
      name: "모험적인유저",
      avatar: "/placeholder.svg?height=32&width=32",
    },
    command: "/모험",
    details: "성공 - 50 꿀 획득",
  },
  {
    id: "LOG002",
    timestamp: "2025-06-29 10:28:45",
    user: {
      name: "관대한기부자",
      avatar: "/placeholder.svg?height=32&width=32",
    },
    command: "/허니선물",
    details: "모험적인유저에게 100 꿀 선물",
  },
  {
    id: "LOG003",
    timestamp: "2025-06-28 10:25:02",
    user: {
      name: "새로운참가자",
      avatar: "/placeholder.svg?height=32&width=32",
    },
    command: "/가입",
    details: "신규 가입 완료",
  },
  {
    id: "LOG004",
    timestamp: "2025-06-28 10:20:11",
    user: {
      name: "모험적인유저",
      avatar: "/placeholder.svg?height=32&width=32",
    },
    command: "/모험",
    details: "실패 - 20 꿀 잃음",
  },
  {
    id: "LOG005",
    timestamp: "2025-06-27 10:15:55",
    user: {
      name: "관리자마스터",
      avatar: "/placeholder.svg?height=32&width=32",
    },
    command: "/지급",
    details: "관대한기부자에게 1000 꿀 지급",
  },
]

export default function LogsPage() {
  const [userFilter, setUserFilter] = React.useState("")
  const [commandFilter, setCommandFilter] = React.useState("all")
  const [date, setDate] = React.useState<DateRange | undefined>()

  const uniqueCommands = ["all", ...Array.from(new Set(logs.map((log) => log.command)))]

  const filteredLogs = React.useMemo(() => {
    return logs.filter((log) => {
      const logDate = new Date(log.timestamp)
      const from = date?.from
      const to = date?.to ? new Date(date.to.getTime() + 86400000 - 1) : undefined // include the whole day

      const dateMatch = !from || !to || (logDate >= from && logDate <= to)
      const userMatch = log.user.name.toLowerCase().includes(userFilter.toLowerCase())
      const commandMatch = commandFilter === "all" || log.command === commandFilter

      return dateMatch && userMatch && commandMatch
    })
  }, [userFilter, commandFilter, date])

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center">
        <h1 className="text-lg font-semibold md:text-2xl">봇 사용 로그</h1>
      </div>
      <div className="flex flex-col md:flex-row items-center gap-4">
        <div className="flex-1 w-full md:w-auto">
          <Input
            placeholder="사용자 이름으로 검색..."
            value={userFilter}
            onChange={(e) => setUserFilter(e.target.value)}
            className="w-full"
          />
        </div>
        <Select value={commandFilter} onValueChange={setCommandFilter}>
          <SelectTrigger className="w-full md:w-[180px]">
            <SelectValue placeholder="명령어 선택" />
          </SelectTrigger>
          <SelectContent>
            {uniqueCommands.map((command) => (
              <SelectItem key={command} value={command}>
                {command === "all" ? "모든 명령어" : command}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Popover>
          <PopoverTrigger asChild>
            <Button
              id="date"
              variant={"outline"}
              className={cn(
                "w-full md:w-[260px] justify-start text-left font-normal",
                !date && "text-muted-foreground",
              )}
            >
              <CalendarIcon className="mr-2 h-4 w-4" />
              {date?.from ? (
                date.to ? (
                  <>
                    {format(date.from, "yyyy-MM-dd")} - {format(date.to, "yyyy-MM-dd")}
                  </>
                ) : (
                  format(date.from, "yyyy-MM-dd")
                )
              ) : (
                <span>날짜 범위 선택</span>
              )}
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-auto p-0" align="end">
            <Calendar
              initialFocus
              mode="range"
              defaultMonth={date?.from}
              selected={date}
              onSelect={setDate}
              numberOfMonths={2}
            />
          </PopoverContent>
        </Popover>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>최근 활동</CardTitle>
          <CardDescription>서버에서 발생한 봇 명령어 사용 기록입니다.</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="hidden sm:table-cell">시간</TableHead>
                <TableHead>사용자</TableHead>
                <TableHead>명령어</TableHead>
                <TableHead>세부 정보</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredLogs.length > 0 ? (
                filteredLogs.map((log) => (
                  <TableRow key={log.id}>
                    <TableCell className="hidden sm:table-cell text-sm text-muted-foreground">
                      {log.timestamp}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Image
                          src={log.user.avatar || "/placeholder.svg"}
                          width={28}
                          height={28}
                          alt="User Avatar"
                          className="rounded-full"
                        />
                        <span className="font-medium">{log.user.name}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{log.command}</Badge>
                    </TableCell>
                    <TableCell>{log.details}</TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={4} className="h-24 text-center">
                    검색 결과가 없습니다.
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
