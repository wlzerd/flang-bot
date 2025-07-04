"use client"

import type React from "react"

import Link from "next/link"
import Image from "next/image"
import { usePathname, useRouter } from "next/navigation"
import { Home, Bot, PanelLeft, Search, Swords, Coins, History, Users, ShieldCheck } from "lucide-react"
import { Suspense, useEffect } from "react"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { cn } from "@/lib/utils"
import { Toaster } from "@/components/ui/toaster"

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()
  const router = useRouter()

  const navItems = [
    { href: "/", label: "홈", icon: Home },
    { href: "/users", label: "사용자 목록", icon: Users },
    { href: "/points", label: "포인트 지급", icon: Coins },
    { href: "/dungeon", label: "던전 조정", icon: Swords },
    { href: "/logs", label: "봇 사용 로그", icon: History },
    { href: "/admin-logs", label: "관리자 로그", icon: ShieldCheck },
  ]

  useEffect(() => {
    const loggedIn = localStorage.getItem("loggedIn")
    if (!loggedIn && pathname !== "/login") {
      router.push("/login")
    } else if (loggedIn && pathname === "/login") {
      router.push("/")
    }
  }, [pathname, router])

  const handleLogout = () => {
    // 실제 애플리케이션에서는 로그아웃 API 호출 및 세션 정리 로직이 필요합니다.
    localStorage.removeItem("loggedIn")
    router.push("/login")
  }

  if (pathname === "/login") {
    return <>{children}</>
  }

  return (
    <Suspense>
      <div className="grid min-h-screen w-full md:grid-cols-[220px_1fr] lg:grid-cols-[280px_1fr]">
        <div className="hidden border-r bg-muted/40 md:block">
          <div className="flex h-full max-h-screen flex-col gap-2">
            <div className="flex h-14 items-center border-b px-4 lg:h-[60px] lg:px-6">
              <Link href="/" className="flex items-center gap-2 font-semibold">
                <Bot className="h-6 w-6" />
                <span className="">Flang-Bot 관리자</span>
              </Link>
            </div>
            <div className="flex-1">
              <nav className="grid items-start px-2 text-sm font-medium lg:px-4">
                {navItems.map((item) => (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      "flex items-center gap-3 rounded-lg px-3 py-2 text-muted-foreground transition-all hover:text-primary",
                      pathname === item.href && "bg-muted text-primary",
                    )}
                  >
                    <item.icon className="h-4 w-4" />
                    {item.label}
                  </Link>
                ))}
              </nav>
            </div>
          </div>
        </div>
        <div className="flex flex-col">
          <header className="flex h-14 items-center gap-4 border-b bg-muted/40 px-4 lg:h-[60px] lg:px-6">
            <Sheet>
              <SheetTrigger asChild>
                <Button variant="outline" size="icon" className="shrink-0 md:hidden bg-transparent">
                  <PanelLeft className="h-5 w-5" />
                  <span className="sr-only">네비게이션 메뉴 열기</span>
                </Button>
              </SheetTrigger>
              <SheetContent side="left" className="flex flex-col w-72">
                <nav className="grid gap-2 text-lg font-medium">
                  <Link href="#" className="flex items-center gap-2 text-lg font-semibold mb-4">
                    <Bot className="h-6 w-6" />
                    <span className="">Flang-Bot 관리자</span>
                  </Link>
                  {navItems.map((item) => (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={cn(
                        "mx-[-0.65rem] flex items-center gap-4 rounded-xl px-3 py-2 text-muted-foreground hover:text-foreground",
                        pathname === item.href && "bg-muted text-foreground",
                      )}
                    >
                      <item.icon className="h-5 w-5" />
                      {item.label}
                    </Link>
                  ))}
                </nav>
              </SheetContent>
            </Sheet>
            <div className="w-full flex-1">
              <form>
                <div className="relative">
                  <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    type="search"
                    placeholder="유저 검색..."
                    className="w-full appearance-none bg-background pl-8 shadow-none md:w-2/3 lg:w-1/3"
                  />
                </div>
              </form>
            </div>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="secondary" size="icon" className="rounded-full">
                  <Image
                    src="/placeholder.svg?height=32&width=32"
                    width={32}
                    height={32}
                    alt="User Avatar"
                    className="rounded-full"
                  />
                  <span className="sr-only">사용자 메뉴 토글</span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>관리자 계정</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem>설정</DropdownMenuItem>
                <DropdownMenuItem>지원</DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout}>로그아웃</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </header>
          <main className="flex flex-1 flex-col gap-4 p-4 lg:gap-6 lg:p-6">{children}</main>
        </div>
      </div>
      <Toaster />
    </Suspense>
  )
}
