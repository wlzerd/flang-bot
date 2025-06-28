import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export default function PointsPage() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center">
        <h1 className="text-lg font-semibold md:text-2xl">포인트 지급</h1>
      </div>
      <Card className="w-full max-w-lg">
        <CardHeader>
          <CardTitle>유저에게 포인트 지급</CardTitle>
          <CardDescription>지급할 유저의 ID와 포인트 액수를 입력하세요.</CardDescription>
        </CardHeader>
        <CardContent>
          <form className="grid gap-4">
            <div className="grid gap-2">
              <Label htmlFor="userId">유저 ID</Label>
              <Input id="userId" placeholder="디스코드 유저 ID 또는 이름" required />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="amount">포인트 액수</Label>
              <Input id="amount" type="number" placeholder="예: 1000" required />
            </div>
          </form>
        </CardContent>
        <CardFooter className="border-t px-6 py-4">
          <Button>지급하기</Button>
        </CardFooter>
      </Card>
    </div>
  )
}
