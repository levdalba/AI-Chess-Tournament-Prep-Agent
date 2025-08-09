import { Card, CardHeader, CardContent } from '../components/ui'

export function DashboardPage() {
  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Welcome back! Here's an overview of your chess preparation.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <div className="h-6 w-6 text-blue-600">📊</div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Games Analyzed</p>
                  <p className="text-2xl font-bold text-gray-900">247</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-green-100 rounded-lg">
                  <div className="h-6 w-6 text-green-600">📋</div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Prep Plans</p>
                  <p className="text-2xl font-bold text-gray-900">12</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <div className="h-6 w-6 text-purple-600">🎯</div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Drills Completed</p>
                  <p className="text-2xl font-bold text-gray-900">89</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-yellow-100 rounded-lg">
                  <div className="h-6 w-6 text-yellow-600">⭐</div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Rating</p>
                  <p className="text-2xl font-bold text-gray-900">1847</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card>
            <CardHeader>
              <h2 className="text-xl font-semibold">Recent Activity</h2>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center p-4 bg-gray-50 rounded-lg">
                  <div className="h-2 w-2 bg-green-500 rounded-full mr-3"></div>
                  <div className="flex-1">
                    <p className="font-medium">Analyzed games vs. Player123</p>
                    <p className="text-sm text-gray-600">2 hours ago</p>
                  </div>
                </div>
                <div className="flex items-center p-4 bg-gray-50 rounded-lg">
                  <div className="h-2 w-2 bg-blue-500 rounded-full mr-3"></div>
                  <div className="flex-1">
                    <p className="font-medium">Created prep plan for tournament</p>
                    <p className="text-sm text-gray-600">1 day ago</p>
                  </div>
                </div>
                <div className="flex items-center p-4 bg-gray-50 rounded-lg">
                  <div className="h-2 w-2 bg-purple-500 rounded-full mr-3"></div>
                  <div className="flex-1">
                    <p className="font-medium">Completed daily tactics drill</p>
                    <p className="text-sm text-gray-600">2 days ago</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <h2 className="text-xl font-semibold">Today's Drills</h2>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="p-4 border border-chess-primary/20 bg-chess-primary/5 rounded-lg">
                  <h3 className="font-medium text-chess-primary">Opening Trap Study</h3>
                  <p className="text-sm text-gray-600 mt-1">Study the Smith-Morra Gambit trap</p>
                  <p className="text-xs text-gray-500 mt-2">Difficulty: ★★★☆☆</p>
                </div>
                <div className="p-4 border border-gray-200 rounded-lg">
                  <h3 className="font-medium">Tactical Puzzle</h3>
                  <p className="text-sm text-gray-600 mt-1">Solve knight fork combinations</p>
                  <p className="text-xs text-gray-500 mt-2">Difficulty: ★★☆☆☆</p>
                </div>
                <div className="p-4 border border-gray-200 rounded-lg">
                  <h3 className="font-medium">Endgame Training</h3>
                  <p className="text-sm text-gray-600 mt-1">Practice rook vs pawn endings</p>
                  <p className="text-xs text-gray-500 mt-2">Difficulty: ★★★★☆</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
