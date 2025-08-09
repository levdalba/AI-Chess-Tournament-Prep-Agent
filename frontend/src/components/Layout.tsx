import React from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { 
  ChartBarIcon, 
  HomeIcon, 
  DocumentTextIcon, 
  AcademicCapIcon,
  UserIcon,
  ArrowRightOnRectangleIcon 
} from '@heroicons/react/24/outline'
import { useLogout } from '../hooks/api'

interface LayoutProps {
  children: React.ReactNode
}

export function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const navigate = useNavigate()
  const logoutMutation = useLogout()

  const handleLogout = async () => {
    try {
      await logoutMutation.mutateAsync()
      navigate('/login')
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
    { name: 'Analysis', href: '/analysis', icon: ChartBarIcon },
    { name: 'Prep Plans', href: '/prep-plans', icon: DocumentTextIcon },
    { name: 'Daily Drills', href: '/drills', icon: AcademicCapIcon },
  ]

  const isActive = (href: string) => location.pathname === href

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="flex w-64 flex-col bg-white border-r border-gray-200">
        <div className="flex h-16 items-center px-6 border-b border-gray-200">
          <Link to="/dashboard" className="flex items-center">
            <div className="h-8 w-8 bg-chess-primary rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">♕</span>
            </div>
            <span className="ml-3 text-lg font-semibold text-gray-900">
              Chess Prep
            </span>
          </Link>
        </div>

        <nav className="flex-1 px-4 py-6 space-y-2">
          {navigation.map((item) => (
            <Link
              key={item.name}
              to={item.href}
              className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive(item.href)
                  ? 'bg-chess-primary/10 text-chess-primary border-chess-primary/20 border'
                  : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
              }`}
            >
              <item.icon className="mr-3 h-5 w-5" />
              {item.name}
            </Link>
          ))}
        </nav>

        {/* User menu */}
        <div className="border-t border-gray-200 p-4">
          <div className="flex items-center space-x-3 mb-4">
            <div className="h-8 w-8 bg-gray-300 rounded-full flex items-center justify-center">
              <UserIcon className="h-5 w-5 text-gray-600" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                User Profile
              </p>
              <p className="text-xs text-gray-500 truncate">
                user@example.com
              </p>
            </div>
          </div>
          
          <button
            onClick={handleLogout}
            className="flex w-full items-center px-3 py-2 text-sm font-medium text-gray-700 rounded-lg hover:bg-gray-100 hover:text-gray-900 transition-colors"
            disabled={logoutMutation.isPending}
          >
            <ArrowRightOnRectangleIcon className="mr-3 h-5 w-5" />
            {logoutMutation.isPending ? 'Signing out...' : 'Sign out'}
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  )
}
