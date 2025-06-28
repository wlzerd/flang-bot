"use client"

import { LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from "recharts"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

const data = [
  { month: "1월", joined: 186, left: 80 },
  { month: "2월", joined: 305, left: 200 },
  { month: "3월", joined: 237, left: 120 },
  { month: "4월", joined: 273, left: 190 },
  { month: "5월", joined: 209, left: 130 },
  { month: "6월", joined: 214, left: 140 },
]

export function UserGrowthChart() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>유저 증감 현황</CardTitle>
        <CardDescription>지난 6개월간 디스코드 서버 유저 수 변화</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-[320px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 20, right: 16, left: 0, bottom: 0 }}>
              <CartesianGrid vertical={false} strokeDasharray="3 3" />
              <XAxis dataKey="month" tickLine={false} axisLine={false} />
              <YAxis tickLine={false} axisLine={false} />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="joined"
                name="신규 유저"
                stroke="#10b981" /* emerald-500 */
                strokeWidth={2}
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
              />
              <Line
                type="monotone"
                dataKey="left"
                name="탈퇴 유저"
                stroke="#ef4444" /* red-500 */
                strokeWidth={2}
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
