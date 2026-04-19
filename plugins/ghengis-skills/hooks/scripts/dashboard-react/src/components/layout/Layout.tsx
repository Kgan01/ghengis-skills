import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { BottomNav } from './BottomNav'
import { usePermissions } from '../../hooks/usePermissions'
import { PermissionToast } from '../agent/PermissionToast'

export function Layout() {
  const { permissions, decide } = usePermissions()

  return (
    <div className="flex h-screen">
      <Sidebar />
      <main className="flex-1 p-4 md:p-8 pb-20 md:pb-8 overflow-y-auto scroll-smooth min-h-0">
        <Outlet />
      </main>
      <BottomNav />
      <PermissionToast permissions={permissions} onDecide={decide} />
    </div>
  )
}
