"use client"

import { useEffect, useState } from "react"
import { Line, LineChart, CartesianGrid, XAxis, YAxis } from "recharts"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  ChartLegend,
  ChartLegendContent,
} from "@/components/ui/chart"


const chartConfig = {
  joined: {
    label: "신규 유저",
    color: "hsl(var(--chart-2))",
  },
  left: {
    label: "탈퇴 유저",
    color: "hsl(var(--chart-5))",
  },
}

export function UserGrowthChart() {
  const [data, setData] = useState([])

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/stats/user-growth`)
      .then((res) => res.json())
      .then((d) => setData(d))
      .catch((err) => console.error(err))
  }, [])

  return (
    <Card>
      <CardHeader>
        <CardTitle>유저 증감 현황</CardTitle>
        <CardDescription>지난 6개월간 디스코드 서버 유저 수 변화</CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig} className="h-[320px] w-full">
          <LineChart
            accessibilityLayer
            data={data}
            margin={{
              top: 20,
              right: 16,
              left: 0,
              bottom: 0,
            }}
          >
            <CartesianGrid vertical={false} />
            <XAxis dataKey="month" tickLine={false} axisLine={false} tickMargin={8} />
            <YAxis tickLine={false} axisLine={false} tickMargin={8} />
            <ChartTooltip cursor={false} content={<ChartTooltipContent />} />
            <ChartLegend content={<ChartLegendContent />} />
            <Line
              dataKey="joined"
              type="monotone"
              stroke="var(--color-joined)"
              strokeWidth={2}
              dot={{
                fill: "var(--color-joined)",
              }}
              activeDot={{
                r: 6,
              }}
            />
            <Line
              dataKey="left"
              type="monotone"
              stroke="var(--color-left)"
              strokeWidth={2}
              dot={{
                fill: "var(--color-left)",
              }}
              activeDot={{
                r: 6,
              }}
            />
          </LineChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}
