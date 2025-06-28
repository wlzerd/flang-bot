"use client"

import Image from "next/image"
import { MoreHorizontal } from "lucide-react"
import Link from "next/link"
import { useEffect, useState } from "react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

export default function UsersPage() {
  const [users, setUsers] = useState<any[]>([])

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/users`)
      .then((res) => res.json())
      .then((data) =>
        setUsers(
          data.map((u: any) => ({
            id: u.user_id,
            name: u.name,
            avatar: u.avatar_url,
            joinedDate: new Date(u.joined_at * 1000)
              .toISOString()
              .split("T")[0],
            points: u.honey,
            status: u.registered_at > 0 ? "registered" : "unregistered",
          }))
        )
      )
      .catch((err) => console.error(err))
  }, [])
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center">
        <h1 className="text-lg font-semibold md:text-2xl">사용자 목록</h1>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>전체 사용자</CardTitle>
          <CardDescription>서버에 가입한 모든 사용자 목록입니다.</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>사용자</TableHead>
                <TableHead className="hidden md:table-cell">가입일</TableHead>
                <TableHead className="hidden md:table-cell">보유 꿀</TableHead>
                <TableHead>상태</TableHead>
                <TableHead>
                  <span className="sr-only">Actions</span>
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell className="font-medium">
                    <Link href={`/users/${user.id}`} className="flex items-center gap-3 hover:underline">
                      <Image
                        src={user.avatar || "/placeholder.svg"}
                        width={32}
                        height={32}
                        alt={`${user.name}'s avatar`}
                        className="rounded-full"
                      />
                      <span>{user.name}</span>
                    </Link>
                  </TableCell>
                  <TableCell className="hidden md:table-cell">{user.joinedDate}</TableCell>
                  <TableCell className="hidden md:table-cell">{user.points.toLocaleString()} 꿀</TableCell>
                  <TableCell>
                    <Badge variant={user.status === "registered" ? "secondary" : "outline"}>
                      {user.status === "registered" ? "등록됨" : "미등록"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button aria-haspopup="true" size="icon" variant="ghost">
                          <MoreHorizontal className="h-4 w-4" />
                          <span className="sr-only">메뉴 토글</span>
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuLabel>작업</DropdownMenuLabel>
                        <DropdownMenuItem>정보 수정</DropdownMenuItem>
                        <DropdownMenuItem>포인트 조정</DropdownMenuItem>
                        <DropdownMenuItem className="text-destructive">사용자 추방</DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
